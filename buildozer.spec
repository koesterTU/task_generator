[app]
title = Task Generator
package.name = taskgenerator
package.domain = org.example
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,otf
version = 0.1
requirements = python3,kivy,libffi
orientation = portrait
fullscreen = 0
entrypoint = main.py
include_patterns = fonts/*

android.api = 33
android.minapi = 21
android.ndk = 25b
android.build_tools_version = 33.0.2

# 自动接受 SDK 协议（GitHub Actions 用）
android.accept_sdk_license = True
android.sdk_extra_args = --accept-sdk-license
