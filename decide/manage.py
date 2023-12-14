#!/usr/bin/env python
import os
import sys

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "decide.settings")
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    if sys.argv[1] == "test":
        os.environ["RECAPTCHA_PUBLIC_KEY"] = "6LeIxAcTAAAAAJcZVRqyHh71UMIEGNQ_MXjiZKhI"
        os.environ["RECAPTCHA_PRIVATE_KEY"] = "6LeIxAcTAAAAAGG-vFI1TnRWxMZNFuojJ4WifJWe"

        # Disable recaptcha
        os.environ["DISABLE_RECAPTCHA"] = "1"
    execute_from_command_line(sys.argv)
