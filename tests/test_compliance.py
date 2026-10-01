import pickle

from funlanzou.gui import config as config_module


def test_credentials_are_written_to_funsecret_not_pickle(monkeypatch):
    secrets = {}

    def write_secret(value, *path):
        secrets[path] = value

    def read_secret(*path):
        return secrets.get(path)

    monkeypatch.setattr(config_module, "write_secret", write_secret)
    monkeypatch.setattr(config_module, "read_secret", read_secret)
    monkeypatch.setattr(config_module, "save_config", lambda config: None)

    config = config_module.Config()
    config.set_infos({
        "name": "audit-user",
        "pwd": "audit-password",
        "cookie": {"session": "audit-cookie"},
    })

    assert config.pwd == "audit-password"
    assert config.cookie == {"session": "audit-cookie"}
    serialized = pickle.dumps(config)
    assert b"audit-password" not in serialized
    assert b"audit-cookie" not in serialized


def test_legacy_credentials_are_removed_after_migration(monkeypatch):
    secrets = {}
    monkeypatch.setattr(
        config_module,
        "write_secret",
        lambda value, *path: secrets.__setitem__(path, value),
    )

    def legacy_encode(value):
        result = bytearray()
        for byte in value.encode("utf-8"):
            encoded = byte ^ config_module.KEY
            result.extend((encoded % 19 + 46, encoded // 19 + 46))
        return result.decode("utf-8")

    config = config_module.Config()
    config._credentials_migrated = False
    config._name = legacy_encode("legacy-user")
    config._pwd = legacy_encode("legacy-password")
    config._cookie = {"session": legacy_encode("legacy-cookie")}
    config._users[config._name] = (
        config._cookie,
        config._name,
        config._pwd,
        -1,
        config.settings,
    )

    assert config.migrate_credentials() is True
    serialized = pickle.dumps(config)
    assert b"legacy-password" not in serialized
    assert b"legacy-cookie" not in serialized
    assert config._pwd == ""
    assert config._cookie == ""


def test_sensitive_response_values_are_not_logged():
    source = open(config_module.__file__.replace("gui/config.py", "api/core.py"), encoding="utf-8").read()
    assert 'logger.debug(f"Set Cookie: acw_sc__v2=' not in source
    assert "filemoreajax.php post.text=" not in source
    assert "filemoreajax.php resp=" not in source
