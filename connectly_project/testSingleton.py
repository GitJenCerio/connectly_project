from singletons.config_manager import ConfigManager

config1 = ConfigManager()
config2 = ConfigManager()

if config1 is config2:
    print("✅ Singleton works! Both instances are the same.")
else:
    print("❌ Singleton failed. Instances are different.")

config1.set_setting("DEFAULT_PAGE_SIZE", 50)
if config2.get_setting("DEFAULT_PAGE_SIZE") == 50:
    print("✅ Shared state works! Setting was shared across instances.")
else:
    print("❌ Shared state failed.")
