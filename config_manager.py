import json
import os

CONFIG_FILE = 'config.json'


def load_config():
    if not os.path.exists(CONFIG_FILE):
        # 如果配置文件不存在，创建一个默认的
        default_config = {
            "rules": {"image/png": "图片"},
            "settings": {"last_source_dir": "", "last_dest_dir": ""}
        }
        save_config(default_config)
        return default_config

    with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_config(config_data):
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(config_data, f, indent=4, ensure_ascii=False)


def get_rules():
    config = load_config()
    return config.get('rules', {})


def save_rules(rules_dict):
    config = load_config()
    config['rules'] = rules_dict
    save_config(config)