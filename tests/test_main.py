from pytest import raises

from botbot.botbot import main

def test_main_method_no_args():
    # CAN YOU HANDLE IT
    with raises(SystemExit) as exc_info:
        main()
        assert exc_info.value.errno == 2
