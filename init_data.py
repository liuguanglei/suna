import sys
# sys.path.append("../backend")
# from backend.flags.flags import FeatureFlagManager
# from flags.flags import FeatureFlagManager
from cryptography.fernet import Fernet


async def init_data():
    ffm = FeatureFlagManager()
    flags = await ffm.list_flags()
    print(flags)
    if not flags:
        await ffm.set_flag("custom_agents", True, "")
        await ffm.set_flag("agent_marketplace", True, "")
        await ffm.set_flag("workflows", True, "")

    flags = await ffm.list_flags()
    print(flags)


def generate_encryption_key():
    """Generate a new Fernet encryption key"""
    key = Fernet.generate_key()
    return key.decode()


if __name__ == "__main__":
    key = generate_encryption_key()
    print(key)

    # import asyncio
    # asyncio.run(init_data())
