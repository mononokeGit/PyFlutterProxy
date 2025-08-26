#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Python script to setup Flutter project proxy
将PowerShell脚本转换为Python实现，并添加下载进度显示功能
"""

import os
import sys
import re
import requests
from pathlib import Path
from urllib.parse import urlparse
from tqdm import tqdm
import zipfile


class FlutterProxySetup:
    def __init__(self):
        self.script_dir = Path(__file__).parent.absolute()
        self.repositories_to_add = '''        maven { url = uri("https://maven.aliyun.com/repository/gradle-plugin") }
        maven { url = uri("https://maven.aliyun.com/repository/google") }
        maven { url = uri("https://maven.aliyun.com/repository/public") }'''
    
    def print_success(self, message):
        """打印成功信息"""
        print(f"✅ {message}")
    
    def print_error(self, message):
        """打印错误信息"""
        print(f"❌ {message}")
    
    def print_info(self, message):
        """打印信息"""
        print(f"ℹ️  {message}")
    
    def modify_build_gradle_kts(self):
        """修改 android/build.gradle.kts 文件"""
        build_gradle_kts_path = self.script_dir / "android" / "build.gradle.kts"
        
        if not build_gradle_kts_path.exists():
            self.print_error("android/build.gradle.kts not found!")
            return False
        
        try:
            with open(build_gradle_kts_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if 'maven.aliyun.com' not in content:
                content = content.replace('repositories {', f'repositories {{\n{self.repositories_to_add}')
                
                with open(build_gradle_kts_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                self.print_success("Updated android/build.gradle.kts with Aliyun repositories.")
            else:
                self.print_info("Aliyun repositories already exist in android/build.gradle.kts.")
            
            return True
        except Exception as e:
            self.print_error(f"Failed to modify android/build.gradle.kts: {e}")
            return False
    
    def modify_settings_gradle_kts(self):
        """修改 android/settings.gradle.kts 文件"""
        settings_gradle_kts_path = self.script_dir / "android" / "settings.gradle.kts"
        
        if not settings_gradle_kts_path.exists():
            self.print_error("android/settings.gradle.kts not found!")
            return False
        
        try:
            with open(settings_gradle_kts_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if 'maven.aliyun.com' not in content:
                content = content.replace('repositories {', f'repositories {{\n{self.repositories_to_add}')
                
                with open(settings_gradle_kts_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                self.print_success("Updated android/settings.gradle.kts with Aliyun repositories.")
            else:
                self.print_info("Aliyun repositories already exist in android/settings.gradle.kts.")
            
            return True
        except Exception as e:
            self.print_error(f"Failed to modify android/settings.gradle.kts: {e}")
            return False
    
    def download_with_progress(self, url, local_path):
        """带进度条的文件下载"""
        try:
            # 发送HEAD请求获取文件大小
            response = requests.head(url, allow_redirects=True)
            total_size = int(response.headers.get('content-length', 0))
            
            # 开始下载
            response = requests.get(url, stream=True, headers={'User-Agent': 'Python Script'})
            response.raise_for_status()
            
            # 创建进度条
            progress_bar = tqdm(
                total=total_size,
                unit='B',
                unit_scale=True,
                unit_divisor=1024,
                desc=f"下载 {Path(url).name}"
            )
            
            with open(local_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        progress_bar.update(len(chunk))
            
            progress_bar.close()
            
            # 验证下载的文件
            if local_path.exists() and local_path.stat().st_size > 0:
                # 检查是否为有效的zip文件
                try:
                    with zipfile.ZipFile(local_path, 'r') as zip_ref:
                        # 如果能成功打开zip文件，说明文件有效
                        pass
                    
                    file_size_mb = local_path.stat().st_size / (1024 * 1024)
                    self.print_success(f"下载完成! 文件大小: {file_size_mb:.2f} MB")
                    return True
                except zipfile.BadZipFile:
                    self.print_error("Downloaded file is not a valid zip file")
                    local_path.unlink()
                    return False
            else:
                self.print_error("Downloaded file is empty or not found")
                if local_path.exists():
                    local_path.unlink()
                return False
                
        except requests.RequestException as e:
            self.print_error(f"Failed to download file: {e}")
            if local_path.exists():
                local_path.unlink()
            return False
        except Exception as e:
            self.print_error(f"Unexpected error during download: {e}")
            if local_path.exists():
                local_path.unlink()
            return False
    
    def modify_gradle_wrapper_properties(self):
        """修改 android/gradle/wrapper/gradle-wrapper.properties 文件"""
        gradle_wrapper_properties_path = self.script_dir / "android" / "gradle" / "wrapper" / "gradle-wrapper.properties"
        
        if not gradle_wrapper_properties_path.exists():
            self.print_error("android/gradle/wrapper/gradle-wrapper.properties not found!")
            return False
        
        try:
            with open(gradle_wrapper_properties_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            distribution_url = None
            for line in lines:
                if line.strip().startswith('distributionUrl='):
                    distribution_url = line.strip().split('=', 1)[1]
                    break
            
            if not distribution_url:
                self.print_error("distributionUrl not found in gradle-wrapper.properties")
                return False
            
            # 检查是否已经是本地文件路径
            if distribution_url.startswith('file://'):
                self.print_info(f"gradle-wrapper.properties already configured for local distribution: {distribution_url}")
                return True
            
            if distribution_url.startswith('https'):
                # 处理转义的冒号
                distribution_url = distribution_url.replace('https\\:', 'https:')
                distribution_url = distribution_url.replace('services.gradle.org/distributions', 'mirrors.cloud.tencent.com/gradle')
                
                local_gradle_dist_path = self.script_dir / "gradle-dist"
                file_name = Path(urlparse(distribution_url).path).name
                local_file_path = local_gradle_dist_path / file_name
                
                # 创建目录
                local_gradle_dist_path.mkdir(exist_ok=True)
                
                # 检查文件是否已存在
                if local_file_path.exists():
                    self.print_info(f"Gradle distribution already exists locally: {local_file_path}")
                else:
                    self.print_info(f"Downloading gradle distribution from {distribution_url}...")
                    
                    if not self.download_with_progress(distribution_url, local_file_path):
                        self.print_error("Flutter project setup completed with errors.")
                        return False
                
                # 验证文件是否存在并更新配置
                if local_file_path.exists():
                    # 将Windows路径转换为正确的file URI格式
                    normalized_path = str(local_file_path).replace('\\', '/')
                    
                    # 确保路径以正确的file URI格式开始
                    if re.match(r'^[A-Za-z]:', normalized_path):
                        new_distribution_url = f"file:///{normalized_path}"
                    else:
                        new_distribution_url = f"file://{normalized_path}"
                    
                    # 更新配置文件
                    updated_lines = []
                    for line in lines:
                        if line.strip().startswith('distributionUrl='):
                            old_line = line.strip()
                            updated_lines.append(f"distributionUrl={new_distribution_url}\n")
                            self.print_info(f"Updated distributionUrl from: {old_line}")
                            self.print_info(f"Updated distributionUrl to: distributionUrl={new_distribution_url}")
                        else:
                            updated_lines.append(line)
                    
                    # 写回文件
                    with open(gradle_wrapper_properties_path, 'w', encoding='utf-8') as f:
                        f.writelines(updated_lines)
                    
                    self.print_success(f"Updated gradle-wrapper.properties to use local gradle distribution: {new_distribution_url}")
                else:
                    self.print_error(f"Downloaded file not found at {local_file_path}. Configuration not updated.")
                    return False
            
            return True
        except Exception as e:
            self.print_error(f"Failed to modify gradle-wrapper.properties: {e}")
            return False
    
    def run(self):
        """运行主程序"""
        print("🚀 Starting Flutter project proxy setup...")
        print("="*50)
        
        success = True
        
        # 修改 android/build.gradle.kts
        if not self.modify_build_gradle_kts():
            success = False
        
        # 修改 android/settings.gradle.kts
        if not self.modify_settings_gradle_kts():
            success = False
        
        # 修改 gradle-wrapper.properties
        if not self.modify_gradle_wrapper_properties():
            success = False
        
        print("="*50)
        if success:
            self.print_success("Flutter project setup complete!")
        else:
            self.print_error("Flutter project setup completed with some errors.")
        
        return success


if __name__ == "__main__":
    setup = FlutterProxySetup()
    success = setup.run()
    sys.exit(0 if success else 1)