import json
import os
import random
import subprocess

CONFIG_GENERATED = "/reforger/Configs/docker_generated.json"


def env_defined(key):
    return key in os.environ and len(os.environ[key]) > 0


def random_passphrase():
    password = "'"
    while "'" in password:
        with open("/usr/share/dict/american-english") as f:
            words = f.readlines()
        password = "-".join(random.sample(words, 3)).replace("\n", "").lower()
    return password


def bool_str(text):
    return text.lower() == "true"


if os.environ["SKIP_INSTALL"] in ["", "false"]:
    steamcmd = ["/steamcmd/steamcmd.sh"]
    steamcmd.extend(["+force_install_dir", "/reforger"])
    if env_defined("STEAM_USER"):
        steamcmd.extend(
            ["+login", os.environ["STEAM_USER"], os.environ["STEAM_PASSWORD"]]
        )
    else:
        steamcmd.extend(["+login", "anonymous"])
    steamcmd.extend(["+app_update", "1874900"])
    if env_defined("STEAM_BRANCH"):
        steamcmd.extend(["-beta", os.environ["STEAM_BRANCH"]])
    if env_defined("STEAM_BRANCH_PASSWORD"):
        steamcmd.extend(["-betapassword", os.environ["STEAM_BRANCH_PASSWORD"]])
    steamcmd.extend(["validate", "+quit"])
    subprocess.call(steamcmd)

if os.environ["ARMA_CONFIG"] != "docker_generated":
    config_path = f"/reforger/Configs/{os.environ['ARMA_CONFIG']}"
else:
    if os.path.exists(CONFIG_GENERATED):
        f = open(CONFIG_GENERATED)
        config = json.load(f)
        f.close()
    else:
        f = open("/docker_default.json")
        config = json.load(f)
        f.close()

    if env_defined("SERVER_BIND_ADDRESS"):
        config["bindAddress"] = os.environ["SERVER_BIND_ADDRESS"]
    if env_defined("SERVER_BIND_PORT"):
        config["bindPort"] = int(os.environ["SERVER_BIND_PORT"])
    if env_defined("SERVER_PUBLIC_ADDRESS"):
        config["publicAddress"] = os.environ["SERVER_PUBLIC_ADDRESS"]
    if env_defined("SERVER_PUBLIC_PORT"):
        config["publicPort"] = int(os.environ["SERVER_PUBLIC_PORT"])
    if env_defined("SERVER_A2S_ADDRESS") and env_defined("SERVER_A2S_PORT"):
        config["a2s"] = {
            "address": os.environ["SERVER_A2S_ADDRESS"],
            "port": int(os.environ["SERVER_A2S_PORT"]),
        }
    else:
        config["a2s"] = None

    if env_defined("GAME_NAME"):
        config["game"]["name"] = os.environ["GAME_NAME"]
    if env_defined("GAME_PASSWORD"):
        config["game"]["password"] = os.environ["GAME_PASSWORD"]
    if env_defined("GAME_PASSWORD_ADMIN"):
        config["game"]["passwordAdmin"] = os.environ["GAME_PASSWORD_ADMIN"]
    else:
        adminPassword = random_passphrase()
        config["game"]["passwordAdmin"] = adminPassword
        print(f"Admin password: {adminPassword}")
    if env_defined("GAME_SCENARIO_ID"):
        config["game"]["scenarioId"] = os.environ["GAME_SCENARIO_ID"]
    if env_defined("GAME_MAX_PLAYERS"):
        config["game"]["maxPlayers"] = int(os.environ["GAME_MAX_PLAYERS"])
    if env_defined("GAME_VISIBLE"):
        config["game"]["visible"] = bool_str(os.environ["GAME_VISIBLE"])
    if env_defined("GAME_SUPPORTED_PLATFORMS"):
        config["game"]["supportedPlatforms"] = os.environ[
            "GAME_SUPPORTED_PLATFORMS"
        ].split(",")
    if env_defined("GAME_PROPS_BATTLEYE"):
        config["game"]["gameProperties"]["battlEye"] = bool_str(
            os.environ["GAME_PROPS_BATTLEYE"]
        )
    if env_defined("GAME_PROPS_DISABLE_THIRD_PERSON"):
        config["game"]["gameProperties"]["disableThirdPerson"] = bool_str(
            os.environ["GAME_PROPS_DISABLE_THIRD_PERSON"]
        )
    if env_defined("GAME_PROPS_FAST_VALIDATION"):
        config["game"]["gameProperties"]["fastValidation"] = bool_str(
            os.environ["GAME_PROPS_FAST_VALIDATION"]
        )
    if env_defined("GAME_PROPS_SERVER_MAX_VIEW_DISTANCE"):
        config["game"]["gameProperties"]["serverMaxViewDistance"] = int(
            os.environ["GAME_PROPS_SERVER_MAX_VIEW_DISTANCE"]
        )
    if env_defined("GAME_PROPS_SERVER_MIN_GRASS_DISTANCE"):
        config["game"]["gameProperties"]["serverMinGrassDistance"] = int(
            os.environ["GAME_PROPS_SERVER_MIN_GRASS_DISTANCE"]
        )
    if env_defined("GAME_PROPS_NETWORK_VIEW_DISTANCE"):
        config["game"]["gameProperties"]["networkViewDistance"] = int(
            os.environ["GAME_PROPS_NETWORK_VIEW_DISTANCE"]
        )

    f = open(CONFIG_GENERATED, "w")
    json.dump(config, f, indent=4)
    f.close()

    config_path = CONFIG_GENERATED

launch = " ".join(
    [
        os.environ["ARMA_BINARY"],
        f"-config {config_path}",
        "-backendlog",
        "-nothrow",
        f"-maxFPS {os.environ['ARMA_MAX_FPS']}",
        f"-profile {os.environ['ARMA_PROFILE']}",
        os.environ["ARMA_PARAMS"],
    ]
)
print(launch, flush=True)
os.system(launch)
