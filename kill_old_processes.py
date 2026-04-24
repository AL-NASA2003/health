import subprocess

pids_to_kill = [29464, 15600, 39176, 17336]

print("=" * 60)
print("正在终止占用 5000 端口的进程...")
print("=" * 60)

for pid in pids_to_kill:
    try:
        print(f"正在终止 PID {pid}...")
        subprocess.run(f"taskkill /PID {pid} /F", shell=True, capture_output=True, text=True)
        print(f"✅ 成功终止 PID {pid}")
    except Exception as e:
        print(f"❌ 终止 PID {pid} 失败: {e}")

print("\n" + "=" * 60)
print("完成！")
print("=" * 60)
