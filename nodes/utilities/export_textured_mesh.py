#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
AutoFlow Export Textured Mesh Node
使用 Hunyuan3D 的导出逻辑，确保法线和纹理正确
"""

import os
import torch
import numpy as np
from pathlib import Path
import folder_paths
from PIL import Image
import tempfile
import shutil

class AutoFlowExportTexturedMesh:
    """
    导出带纹理的 3D 模型（使用 Hunyuan3D 的方法）
    - GLB: 使用 pygltflib 创建 PBR 材质，纹理嵌入
    - OBJ: 保存 OBJ + MTL + 纹理图片
    
    ⚠️ 重要提示：
    - normal_texture 输入通常应该留空
    - Hunyuan3D MultiViews Generator 的 "normals" 输出是多视角法线贴图，不是用于导出的 Normal Map
    - 如果连接了 normal_texture 导致 Blender 中出现 Shading 问题，请断开连接
    """
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "trimesh": ("TRIMESH",),
                "filename_prefix": ("STRING", {"default": "3D/textured_model"}),
                "file_format": (["glb", "obj"],),
            },
            "optional": {
                "albedo_texture": ("IMAGE",),      # Albedo/Base Color 纹理
                "mr_texture": ("IMAGE",),          # Metallic-Roughness 纹理
                "normal_texture": ("IMAGE",),      # Normal Map（通常不需要！）
                "save_file": ("BOOLEAN", {"default": True}),
            },
        }
    
    RETURN_TYPES = ("STRING", "STRING", "STRING", "STRING")
    RETURN_NAMES = ("mesh_path", "albedo_path", "mr_path", "normal_path")
    FUNCTION = "export_textured_mesh"
    CATEGORY = "AutoFlow/Utilities"
    OUTPUT_NODE = True
    
    def export_textured_mesh(self, trimesh, filename_prefix, file_format,
                            albedo_texture=None, mr_texture=None, normal_texture=None,
                            save_file=True):
        """
        导出带纹理的 3D 模型
        
        Args:
            trimesh: 3D 网格对象（trimesh.Trimesh）
            filename_prefix: 文件名前缀
            file_format: 导出格式（glb 或 obj）
            albedo_texture: Albedo 纹理张量 [B, H, W, C]
            mr_texture: Metallic-Roughness 纹理张量
            normal_texture: Normal Map 纹理张量（⚠️ 通常不需要！）
                           注意：这不是 Hunyuan3D MultiViews Generator 的 normals 输出！
                           那个 normals 是多视角法线贴图，不是用于导出的 Normal Map。
                           Hunyuan3D 默认不使用 Normal Map 纹理。
            save_file: 是否保存文件
            
        Returns:
            (mesh_path, albedo_path, mr_path, normal_path): 导出文件的路径
        """
        if not save_file:
            return ("", "", "", "")
        
        # 警告：如果使用了 normal_texture，可能导致 Shading 问题
        if normal_texture is not None:
            print("⚠️ 警告：检测到 normal_texture 输入")
            print("   如果 Blender 中出现 Shading 问题（明暗不一致），请断开 normal_texture 连接")
            print("   Hunyuan3D 默认不使用 Normal Map 纹理")
            print("   MultiViews Generator 的 'normals' 输出不应该连接到这里")
        
        # 获取输出路径
        full_output_folder, filename, counter, subfolder, _ = \
            folder_paths.get_save_image_path(filename_prefix, folder_paths.get_output_directory())
        
        output_folder = Path(full_output_folder)
        output_folder.mkdir(parents=True, exist_ok=True)
        
        # 构建文件名
        base_name = f'{filename}_{counter:05}_'
        
        # 初始化返回路径
        albedo_path = ""
        mr_path = ""
        normal_path = ""
        
        if file_format == "glb":
            # GLB 格式：使用 Hunyuan3D 的方法
            mesh_path, albedo_path, mr_path, normal_path = self._export_glb_hunyuan_style(
                trimesh, output_folder, base_name,
                albedo_texture, mr_texture, normal_texture
            )
        else:
            # OBJ 格式：保存纹理文件
            mesh_path, albedo_path, mr_path, normal_path = self._export_obj_with_textures(
                trimesh, output_folder, base_name,
                albedo_texture, mr_texture, normal_texture
            )
        
        # 返回相对路径
        mesh_relative = str(Path(subfolder) / Path(mesh_path).name) if mesh_path else ""
        albedo_relative = str(Path(subfolder) / Path(albedo_path).name) if albedo_path else ""
        mr_relative = str(Path(subfolder) / Path(mr_path).name) if mr_path else ""
        normal_relative = str(Path(subfolder) / Path(normal_path).name) if normal_path else ""
        
        print(f"✓ 已导出带纹理的模型: {mesh_relative}")
        if albedo_relative:
            print(f"  - Albedo 纹理: {albedo_relative}")
        if mr_relative:
            print(f"  - MR 纹理: {mr_relative}")
        if normal_relative:
            print(f"  - Normal 纹理: {normal_relative}")
        
        return (mesh_relative, albedo_relative, mr_relative, normal_relative)
    
    def _export_glb_hunyuan_style(self, trimesh_obj, output_folder, base_name,
                                   albedo_texture, mr_texture, normal_texture):
        """
        使用 Hunyuan3D 的方法导出 GLB
        步骤：
        1. 先导出 OBJ + 纹理
        2. 使用 pygltflib 转换为 GLB（保留法线）
        
        Args:
            trimesh_obj: trimesh.Trimesh 对象
            output_folder: 输出文件夹
            base_name: 文件基础名
            albedo_texture: Albedo 纹理
            mr_texture: MR 纹理
            normal_texture: Normal 纹理
            
        Returns:
            tuple: (glb_path, albedo_path, mr_path, normal_path)
        """
        import trimesh
        import pygltflib
        import base64
        
        # 创建临时目录
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # 步骤 1: 导出 OBJ（保留原始法线）
            temp_obj = temp_path / "temp.obj"
            trimesh_obj.export(str(temp_obj), file_type='obj')
            
            # 步骤 2: 保存纹理到临时目录
            texture_paths = {}
            albedo_path = ""
            mr_path = ""
            normal_path = ""
            
            if albedo_texture is not None:
                albedo_temp = temp_path / "albedo.png"
                self._save_texture_tensor(albedo_texture, albedo_temp)
                texture_paths['albedo'] = str(albedo_temp)
                
                # 同时保存到输出目录
                albedo_path = str(output_folder / f'{base_name}albedo.png')
                shutil.copy(str(albedo_temp), albedo_path)
            
            if mr_texture is not None:
                mr_temp = temp_path / "mr.png"
                self._save_texture_tensor(mr_texture, mr_temp)
                
                # 分离 Metallic 和 Roughness
                metallic_temp = temp_path / "metallic.png"
                roughness_temp = temp_path / "roughness.png"
                self._split_mr_texture(str(mr_temp), str(metallic_temp), str(roughness_temp))
                
                texture_paths['metallic'] = str(metallic_temp)
                texture_paths['roughness'] = str(roughness_temp)
                
                # 同时保存到输出目录
                mr_path = str(output_folder / f'{base_name}mr.png')
                shutil.copy(str(mr_temp), mr_path)
            
            if normal_texture is not None:
                normal_temp = temp_path / "normal.png"
                self._save_texture_tensor(normal_texture, normal_temp)
                texture_paths['normal'] = str(normal_temp)
                
                # 同时保存到输出目录
                normal_path = str(output_folder / f'{base_name}normal.png')
                shutil.copy(str(normal_temp), normal_path)
            
            # 步骤 3: 使用 Hunyuan3D 的方法转换为 GLB
            glb_path = str(output_folder / f'{base_name}.glb')
            self._create_glb_with_pbr_materials(str(temp_obj), texture_paths, glb_path)
            
            return (glb_path, albedo_path, mr_path, normal_path)
    
    def _create_glb_with_pbr_materials(self, obj_path, textures_dict, output_path):
        """
        使用 pygltflib 创建包含完整 PBR 材质的 GLB 文件
        这是 Hunyuan3D 的方法，确保法线正确
        
        Args:
            obj_path: OBJ 文件路径
            textures_dict: 纹理字典 {'albedo': path, 'metallic': path, 'roughness': path, 'normal': path}
            output_path: 输出 GLB 路径
        """
        import trimesh
        import pygltflib
        import base64
        
        # 1. 加载 OBJ 文件（保留原始法线）
        mesh = trimesh.load(obj_path, process=False)  # process=False 保留原始数据
        
        # 2. 先导出为临时 GLB（保留法线）
        temp_glb = str(Path(output_path).parent / "temp_base.glb")
        mesh.export(temp_glb, file_type='glb')
        
        # 3. 加载 GLB 文件进行材质编辑
        gltf = pygltflib.GLTF2().load(temp_glb)
        
        # 4. 准备纹理数据
        def image_to_data_uri(image_path):
            """将图像转换为 data URI"""
            with open(image_path, "rb") as f:
                image_data = f.read()
            encoded = base64.b64encode(image_data).decode()
            # 检测图片格式
            ext = Path(image_path).suffix.lower()
            mime_type = "image/png" if ext == ".png" else "image/jpeg"
            return f"data:{mime_type};base64,{encoded}"
        
        # 5. 合并 metallic 和 roughness
        if "metallic" in textures_dict and "roughness" in textures_dict:
            mr_combined_path = str(Path(output_path).parent / "mr_combined.png")
            self._combine_metallic_roughness(
                textures_dict["metallic"], 
                textures_dict["roughness"], 
                mr_combined_path
            )
            textures_dict["metallicRoughness"] = mr_combined_path
        
        # 6. 添加图像到 GLTF
        images = []
        textures = []
        
        texture_mapping = {
            "albedo": "baseColorTexture",
            "metallicRoughness": "metallicRoughnessTexture",
            "normal": "normalTexture",
        }
        
        for tex_type, tex_path in textures_dict.items():
            if tex_type in texture_mapping and tex_path and os.path.exists(tex_path):
                # 添加图像
                image = pygltflib.Image(uri=image_to_data_uri(tex_path))
                images.append(image)
                
                # 添加纹理
                texture = pygltflib.Texture(source=len(images) - 1)
                textures.append(texture)
        
        # 7. 创建 PBR 材质
        pbr_metallic_roughness = pygltflib.PbrMetallicRoughness(
            baseColorFactor=[1.0, 1.0, 1.0, 1.0],
            metallicFactor=1.0,
            roughnessFactor=1.0
        )
        
        # 设置纹理索引
        texture_index = 0
        if "albedo" in textures_dict and os.path.exists(textures_dict.get("albedo", "")):
            pbr_metallic_roughness.baseColorTexture = pygltflib.TextureInfo(index=texture_index)
            texture_index += 1
        
        if "metallicRoughness" in textures_dict and os.path.exists(textures_dict.get("metallicRoughness", "")):
            pbr_metallic_roughness.metallicRoughnessTexture = pygltflib.TextureInfo(index=texture_index)
            texture_index += 1
        
        # 创建材质
        material = pygltflib.Material(
            name="PBR_Material",
            pbrMetallicRoughness=pbr_metallic_roughness
        )
        
        # 添加法线贴图（如果有）
        if "normal" in textures_dict and os.path.exists(textures_dict.get("normal", "")):
            material.normalTexture = pygltflib.NormalMaterialTexture(index=texture_index)
            texture_index += 1
        
        # 8. 更新 GLTF
        gltf.images = images
        gltf.textures = textures
        gltf.materials = [material]
        
        # 确保 mesh 使用材质
        if gltf.meshes:
            for primitive in gltf.meshes[0].primitives:
                primitive.material = 0
        
        # 9. 保存最终 GLB
        gltf.save(output_path)
        
        # 清理临时文件
        if os.path.exists(temp_glb):
            os.remove(temp_glb)
        if "metallicRoughness" in textures_dict:
            mr_combined = textures_dict["metallicRoughness"]
            if os.path.exists(mr_combined):
                os.remove(mr_combined)
        
        print(f"✓ PBR GLB 文件已保存: {output_path}")
    
    def _combine_metallic_roughness(self, metallic_path, roughness_path, output_path):
        """
        将 metallic 和 roughness 贴图合并为一张贴图
        GLB 格式要求 metallic 在 B 通道，roughness 在 G 通道
        
        Args:
            metallic_path: Metallic 贴图路径
            roughness_path: Roughness 贴图路径
            output_path: 输出路径
        """
        # 加载贴图
        metallic_img = Image.open(metallic_path).convert("L")  # 转为灰度
        roughness_img = Image.open(roughness_path).convert("L")  # 转为灰度
        
        # 确保尺寸一致
        if metallic_img.size != roughness_img.size:
            roughness_img = roughness_img.resize(metallic_img.size)
        
        # 转为 numpy 数组
        metallic_array = np.array(metallic_img)
        roughness_array = np.array(roughness_img)
        
        # 创建合并的数组 (R, G, B) = (AO, Roughness, Metallic)
        width, height = metallic_img.size
        combined_array = np.zeros((height, width, 3), dtype=np.uint8)
        combined_array[:, :, 0] = 255  # R 通道：AO (如果没有 AO 贴图，设为白色)
        combined_array[:, :, 1] = roughness_array  # G 通道：Roughness
        combined_array[:, :, 2] = metallic_array  # B 通道：Metallic
        
        # 转回 PIL 图像并保存
        combined = Image.fromarray(combined_array)
        combined.save(output_path)
    
    def _split_mr_texture(self, mr_path, metallic_path, roughness_path):
        """
        分离 MR 纹理为 Metallic 和 Roughness
        假设 MR 纹理的 B 通道是 Metallic，G 通道是 Roughness
        
        Args:
            mr_path: MR 纹理路径
            metallic_path: 输出 Metallic 路径
            roughness_path: 输出 Roughness 路径
        """
        mr_img = Image.open(mr_path).convert("RGB")
        mr_array = np.array(mr_img)
        
        # 提取通道（假设 B=Metallic, G=Roughness）
        metallic_array = mr_array[:, :, 2]  # B 通道
        roughness_array = mr_array[:, :, 1]  # G 通道
        
        # 保存为灰度图
        metallic_img = Image.fromarray(metallic_array, mode='L')
        roughness_img = Image.fromarray(roughness_array, mode='L')
        
        metallic_img.save(metallic_path)
        roughness_img.save(roughness_path)
    
    def _export_obj_with_textures(self, trimesh_obj, output_folder, base_name,
                                   albedo_texture, mr_texture, normal_texture):
        """
        导出 OBJ 格式，同时保存纹理文件和 MTL 文件
        
        Args:
            trimesh_obj: trimesh.Trimesh 对象
            output_folder: 输出文件夹
            base_name: 文件基础名
            albedo_texture: Albedo 纹理
            mr_texture: MR 纹理
            normal_texture: Normal 纹理
            
        Returns:
            tuple: (obj_path, albedo_path, mr_path, normal_path)
        """
        mesh_file = output_folder / f'{base_name}.obj'
        mtl_file = output_folder / f'{base_name}.mtl'
        
        albedo_path = ""
        mr_path = ""
        normal_path = ""
        
        # 保存纹理文件
        if albedo_texture is not None:
            albedo_path = str(output_folder / f'{base_name}albedo.png')
            self._save_texture_tensor(albedo_texture, albedo_path)
        
        if mr_texture is not None:
            mr_path = str(output_folder / f'{base_name}mr.png')
            self._save_texture_tensor(mr_texture, mr_path)
        
        if normal_texture is not None:
            normal_path = str(output_folder / f'{base_name}normal.png')
            self._save_texture_tensor(normal_texture, normal_path)
        
        # 导出 OBJ（保留原始法线）
        trimesh_obj.export(str(mesh_file), file_type='obj')
        
        # 创建 MTL 文件
        self._create_mtl_file(
            mtl_file, base_name,
            Path(albedo_path).name if albedo_path else None,
            Path(mr_path).name if mr_path else None,
            Path(normal_path).name if normal_path else None
        )
        
        # 更新 OBJ 文件，添加 MTL 引用
        self._update_obj_with_mtl(mesh_file, mtl_file.name)
        
        return (str(mesh_file), albedo_path, mr_path, normal_path)
    
    def _save_texture_tensor(self, texture_tensor, output_path):
        """
        保存纹理张量为 PNG 图片
        
        Args:
            texture_tensor: 纹理张量 [B, H, W, C] 或 [H, W, C]
            output_path: 输出路径
        """
        # 转换为 numpy 数组
        if torch.is_tensor(texture_tensor):
            texture_np = texture_tensor.cpu().numpy()
        else:
            texture_np = np.array(texture_tensor)
        
        # 处理批次维度
        if len(texture_np.shape) == 4:
            texture_np = texture_np[0]  # 取第一个批次
        
        # 确保值在 [0, 1] 范围
        texture_np = np.clip(texture_np, 0, 1)
        
        # 转换到 [0, 255]
        texture_np = (texture_np * 255).astype(np.uint8)
        
        # 保存为 PNG
        image = Image.fromarray(texture_np)
        image.save(output_path)
    
    def _create_mtl_file(self, mtl_path, base_name, albedo_name, mr_name, normal_name):
        """
        创建 MTL 材质文件
        
        Args:
            mtl_path: MTL 文件路径
            base_name: 材质基础名称
            albedo_name: Albedo 纹理文件名
            mr_name: MR 纹理文件名
            normal_name: Normal 纹理文件名
        """
        with open(mtl_path, 'w', encoding='utf-8') as f:
            f.write(f"# Material file created by AutoFlow\n")
            f.write(f"# PBR Material for {base_name}\n\n")
            f.write(f"newmtl {base_name}material\n")
            
            # 基础属性
            f.write(f"Ka 1.000 1.000 1.000\n")  # Ambient color
            f.write(f"Kd 1.000 1.000 1.000\n")  # Diffuse color
            f.write(f"Ks 0.500 0.500 0.500\n")  # Specular color
            f.write(f"Ns 96.078431\n")           # Specular exponent
            f.write(f"d 1.0\n")                  # Dissolve (transparency)
            f.write(f"illum 2\n")                # Illumination model
            
            # Albedo 纹理（Base Color）
            if albedo_name:
                f.write(f"map_Kd {albedo_name}\n")
            
            # Metallic-Roughness 纹理
            if mr_name:
                f.write(f"map_Ks {mr_name}\n")  # 作为 specular map
                f.write(f"map_Ns {mr_name}\n")  # 作为 roughness map
            
            # Normal Map
            if normal_name:
                f.write(f"map_Bump {normal_name}\n")
                f.write(f"bump {normal_name}\n")
    
    def _update_obj_with_mtl(self, obj_path, mtl_filename):
        """
        更新 OBJ 文件，添加 MTL 引用
        
        Args:
            obj_path: OBJ 文件路径
            mtl_filename: MTL 文件名
        """
        # 读取原始 OBJ 文件
        with open(obj_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # 检查是否已经有 mtllib 声明
        has_mtllib = any(line.startswith('mtllib') for line in lines)
        
        if not has_mtllib:
            # 在文件开头添加 MTL 引用
            with open(obj_path, 'w', encoding='utf-8') as f:
                f.write(f"# OBJ file with PBR textures by AutoFlow\n")
                f.write(f"mtllib {mtl_filename}\n")
                f.write(f"usemtl {Path(mtl_filename).stem}material\n\n")
                f.writelines(lines)

# 节点映射
NODE_CLASS_MAPPINGS = {
    "AutoFlowExportTexturedMesh": AutoFlowExportTexturedMesh,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "AutoFlowExportTexturedMesh": "AutoFlow Export Textured Mesh",
}
