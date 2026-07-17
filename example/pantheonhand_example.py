#!/usr/bin/env python3
"""
PantheonHand20 control example

Features:
- Test PantheonHand20 move_joints_pos and get_joint_positions
- Supports single-hand (right/left) and dual-hand (double) modes
- Joint position control (list and dict formats)
- Command-6 format (single-joint control)
- Rope tightening operations
- Gesture execution and homing operations
- Error handling and resource cleanup
- Log management (enable_all_logs, disable_all_logs, set_log_level, etc.; exercise via test_log_management())

CAN configuration:
- PantheonHand20 communicates over CAN; configure dev_type, channel, arbitration_bitrate, etc.
- Dual-hand mode: right hand on CAN channel 0, left hand on CAN channel 1 (customizable)
- Default: VCI_USBCAN2 (41), 1 Mbps arbitration bitrate

Usage:
1. Configure CAN parameters for your hardware (optional; omit to use defaults)
2. Uncomment the desired test functions in main() to run tests
3. Dual-hand mode requires dual-hand hardware
"""

import time
import sys
import os
import math

# Add project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from hand import create_hand, FingerType

# Import log management utilities
from hand.core import (
    enable_all_logs,
    disable_all_logs,
    set_log_level,
    set_console_only,
    set_file_only,
    set_both_output,
    show_log_status,
    log_controller
)


def get_default_can_config():
    """
    Return default CAN configuration.

    Returns:
        dict: CAN config suitable for create_hand(..., can_config=config)
    """
    return {
        'dev_type': 41,           # VCI_USBCAN2
        'channel': 0,             # CAN channel (0=CAN1, 1=CAN2)
        'arbitration_bitrate': 1000000,  # 1 Mbps arbitration bitrate
        'data_bitrate': 5000000,  # 5 Mbps data bitrate
        'canfd_mode': 0
    }


def test_log_management():
    """Test log management features"""
    print("\n" + "=" * 60)
    print("=== Test log management ===")

    print("\n1. Enable all logs...")
    enable_all_logs()
    print("All logs enabled")

    print("\n2. Set log level to DEBUG...")
    set_log_level('DEBUG')
    print("Log level set to DEBUG")

    print("\n3. Test different output modes...")
    set_console_only()
    print("   Console-only output enabled")
    set_file_only()
    print("   File-only output enabled")
    set_both_output()
    print("   Console + file output enabled")

    print("\n4. Test disabling all logs...")
    disable_all_logs()
    print("All logs disabled")

    print("\n   Test effect after disabling logs (messages below should not appear):")
    from hand.core import get_logger
    test_logger = get_logger('test.disable_logs')
    test_logger.info("This INFO log should not appear")
    test_logger.warning("This WARNING log should not appear")
    test_logger.error("This ERROR log should not appear")
    print("   Disable-log test complete")

    print("\n5. Test per-script log control...")
    log_controller.set_script_logging('pantheonhand.motor', enabled=True, level='WARNING')
    print("Set pantheonhand.motor to WARNING level")

    print("\n6. Current log status:")
    show_log_status()

    print("\n7. Re-enable logs for subsequent tests...")
    enable_all_logs()
    set_log_level('INFO')
    set_both_output()
    print("Logs re-enabled")


def test_pantheonhand20_connection(can_config=None):
    """
    Test PantheonHand20 connection.

    Args:
        can_config: Optional CAN config dict; uses default when None
    """
    print("\n=== Test PantheonHand20 connection ===")

    hand = None
    try:
        hand = create_hand("pantheonhand20", "right", can_config=can_config or {})

        if hand.connect():
            print("PantheonHand20 right hand connected")
            print(f"Connection status: {'connected' if hand.is_connected() else 'disconnected'}")
            print(f"Hand type: {hand.hand_type.value}")
            print(f"Hand side: {hand.hand_side_name}")
            print(f"Is right hand: {hand.is_right_hand}")
            return True
        else:
            print("PantheonHand20 right hand connection failed")
            return False

    except Exception as e:
        print(f"PantheonHand20 connection test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        if hand and hand.is_connected():
            print("Homing...")
            hand.hand_zero()
            time.sleep(1)
            print("Disabling all joints...")
            disable_success = hand.enable_all_motors(False)
            print(f"Disable result: {'succeeded' if disable_success else 'failed'}")
            hand.close()


def test_pantheonhand20_rope_tight(can_config=None):
    """
    Test PantheonHand20 rope tightening.

    Covers: all-finger tighten, single-finger tighten

    Args:
        can_config: Optional CAN config dict
    """
    print("\n=== Test PantheonHand20 rope tightening ===")

    hand = None
    try:
        hand = create_hand("pantheonhand20", "right", can_config=can_config or {})

        if hand.connect():
            print("PantheonHand20 connected, starting rope tightening test")
            time.sleep(1)

            hand.enable_all_motors()
            time.sleep(2)

            print("\n--- Test 1: tighten all fingers ---")
            try:
                hand.rope_tight()
                print("All-finger rope tighten command sent")
                time.sleep(5)
            except Exception as e:
                print(f"All-finger rope tighten failed: {e}")

            print("\n--- Test 2: single-finger rope tighten (thumb) ---")
            try:
                hand.rope_tight(FingerType.THUMB)
                print("Thumb rope tighten command sent")
                time.sleep(3)
            except Exception as e:
                print(f"Thumb rope tighten failed: {e}")

            print("\n--- Test 3: single-finger rope tighten (index) ---")
            try:
                hand.rope_tight(FingerType.INDEX)
                print("Index rope tighten command sent")
                time.sleep(3)
            except Exception as e:
                print(f"Index rope tighten failed: {e}")

            print("\n--- Homing ---")
            success = hand.hand_zero()
            print(f"Homing result: {'succeeded' if success else 'failed'}")

            return True
        else:
            print("PantheonHand20 connection failed")
            return False

    except Exception as e:
        print(f"PantheonHand20 rope tightening test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        if hand and hand.is_connected():
            print("Homing...")
            hand.hand_zero()
            time.sleep(1)
            print("Disabling all joints...")
            disable_success = hand.enable_all_motors(False)
            print(f"Disable result: {'succeeded' if disable_success else 'failed'}")
            hand.close()


def test_pantheonhand20_get_joint_positions(can_config=None):
    """
    Test PantheonHand20 get_joint_positions.

    Args:
        can_config: Optional CAN config dict
    """
    print("\n=== Test PantheonHand20 get_joint_positions ===")

    hand = None
    try:
        hand = create_hand("pantheonhand20", "right", can_config=can_config or {})

        if hand.connect():
            print("PantheonHand20 connected, starting get_joint_positions test")

            print("\n--- Test get all joint positions ---")
            all_positions = hand.get_joint_positions()
            print(f"All joint positions: {all_positions}")
            print(f"Position data type: {type(all_positions)}")
            if hasattr(all_positions, '__len__'):
                print(f"Position data length: {len(all_positions)}")

            return True
        else:
            print("PantheonHand20 connection failed")
            return False

    except Exception as e:
        print(f"PantheonHand20 get_joint_positions test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        if hand and hand.is_connected():
            print("Homing...")
            hand.hand_zero()
            time.sleep(1)
            print("Disabling all joints...")
            disable_success = hand.enable_all_motors(False)
            print(f"Disable result: {'succeeded' if disable_success else 'failed'}")
            hand.close()


def test_pantheonhand20_move_joints_pos_list(can_config=None):
    """
    Test PantheonHand20 move_joints_pos (list format, 15 joints).

    Args:
        can_config: Optional CAN config dict
    """
    print("\n=== Test PantheonHand20 move_joints_pos (list format) ===")

    hand = None
    try:
        hand = create_hand("pantheonhand20", "right", can_config=can_config or {})

        if hand.connect():
            print("PantheonHand20 connected, starting move_joints_pos (list format) test")
            time.sleep(1)

            hand.enable_all_motors()
            time.sleep(2)

            print("\n--- Test 1: set all joints to 0 rad ---")
            zero_positions = [0.0] * 15
            success = hand.move_joints_pos(zero_positions, speed=0.5)
            print(f"Set zero-rad result: {'succeeded' if success else 'failed'}")
            if success:
                time.sleep(2)
                current_positions = hand.get_joint_positions()
                print(f"Current positions: {current_positions}")

            print("\n--- Test 2: set custom positions ---")
            custom_positions = [
                math.radians(40), math.radians(10), math.radians(10),
                0.0, math.radians(10), math.radians(10),
                0.0, math.radians(10), math.radians(10),
                0.0, math.radians(10), math.radians(10),
                0.0, math.radians(10), math.radians(10)
            ]
            success = hand.move_joints_pos(custom_positions, speed=0.5)
            print(f"Set custom positions result: {'succeeded' if success else 'failed'}")
            time.sleep(3)

            print("\n--- Test 3: homing ---")
            success = hand.hand_zero()
            print(f"Homing result: {'succeeded' if success else 'failed'}")
            if success:
                time.sleep(2)
                current_positions = hand.get_joint_positions()
                print(f"Positions after homing: {current_positions}")

            return True
        else:
            print("PantheonHand20 connection failed")
            return False

    except Exception as e:
        print(f"PantheonHand20 move_joints_pos (list format) test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        if hand and hand.is_connected():
            print("Homing...")
            hand.hand_zero()
            time.sleep(1)
            print("Disabling all joints...")
            disable_success = hand.enable_all_motors(False)
            print(f"Disable result: {'succeeded' if disable_success else 'failed'}")
            hand.close()


def test_pantheonhand20_move_joints_pos_dict(can_config=None):
    """
    Test PantheonHand20 move_joints_pos (dict format).

    Covers: dict-format set, command-6 format, per-finger control, homing

    Args:
        can_config: Optional CAN config dict
    """
    print("\n=== Test PantheonHand20 move_joints_pos (dict format) ===")

    hand = None
    try:
        hand = create_hand("pantheonhand20", "right", can_config=can_config or {})

        if hand.connect():
            print("PantheonHand20 connected, starting move_joints_pos (dict format) test")
            time.sleep(1)

            hand.enable_all_motors()
            time.sleep(2)

            print("\n--- Test 1: set right-hand positions in dict format ---")
            right_hand_data = {
                1: [1.5, math.radians(10), math.radians(10)],
                2: [0.0, math.radians(10), math.radians(10)],
                3: [0.0, math.radians(10), math.radians(10)],
                4: [0.0, math.radians(10), math.radians(10)],
                5: [0.0, math.radians(10), math.radians(10)]
            }
            positions_dict = {1: right_hand_data}
            success = hand.move_joints_pos(positions_dict, speed=0.01)
            print(f"Dict-format set result: {'succeeded' if success else 'failed'}")
            if success:
                time.sleep(2)
                print(f"Current positions: {hand.get_joint_positions()}")

            print("\n--- Test 2: command-6 format (single joint control) ---")
            command_6_data = [1, 2, 1, math.radians(30)]  # right hand, index finger, joint 1, 30 deg
            positions_dict = {6: command_6_data}
            success = hand.move_joints_pos(positions_dict, speed=1)
            print(f"Command 6 set result: {'succeeded' if success else 'failed'}")
            if success:
                time.sleep(1)
                print(f"Current positions: {hand.get_joint_positions()}")

            print("\n--- Test 3: per-finger control ---")
            for finger_id in range(1, 6):
                finger_data = {finger_id: [0.0, math.radians(20), math.radians(30)]}
                positions_dict = {1: finger_data}
                success = hand.move_joints_pos(positions_dict, speed=1)
                print(f"Finger {finger_id} control result: {'succeeded' if success else 'failed'}")
                time.sleep(1)

            print("\n--- Test 4: homing ---")
            zero_data = {fid: [0.0, 0.0, 0.0] for fid in range(1, 6)}
            positions_dict = {1: zero_data}
            success = hand.move_joints_pos(positions_dict, speed=1)
            print(f"Homing result: {'succeeded' if success else 'failed'}")

            return True
        else:
            print("PantheonHand20 connection failed")
            return False

    except Exception as e:
        print(f"PantheonHand20 move_joints_pos (dict format) test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        if hand and hand.is_connected():
            print("Homing...")
            hand.hand_zero()
            time.sleep(1)
            print("Disabling all joints...")
            disable_success = hand.enable_all_motors(False)
            print(f"Disable result: {'succeeded' if disable_success else 'failed'}")
            hand.close()


def test_pantheonhand20_double_mode(can_config=None):
    """
    Test PantheonHand20 dual-hand mode.

    Covers: list format, dict format, homing

    Args:
        can_config: Optional dual-hand CAN config; default uses one CAN device for both hands when None
    """
    print("\n=== Test PantheonHand20 dual-hand mode ===")

    hand = None
    try:
        hand = create_hand("pantheonhand20", "double", can_config=can_config or {})

        if hand.connect():
            print("PantheonHand20 dual-hand mode connected")
            time.sleep(1)

            hand.enable_all_motors()
            time.sleep(2)

            print("\n--- Test get dual-hand positions ---")
            all_positions = hand.get_joint_positions()
            print(f"Dual-hand positions: {all_positions}")

            print("\n--- Test dual-hand list format ---")
            right_positions = [math.radians(0)] * 15
            left_positions = [math.radians(-15)] * 15
            double_positions = right_positions + left_positions
            success = hand.move_joints_pos(double_positions, speed=0.5)
            print(f"Dual-hand list-format set result: {'succeeded' if success else 'failed'}")
            if success:
                time.sleep(2)
                print(f"Current positions: {hand.get_joint_positions()}")

            print("\n--- Test dual-hand dict format ---")
            right_hand_data = {
                1: [0.0, math.radians(10), math.radians(10)],
                2: [0.0, math.radians(10), math.radians(10)],
                3: [0.0, math.radians(10), math.radians(10)],
                4: [0.0, math.radians(10), math.radians(10)],
                5: [0.0, math.radians(10), math.radians(10)]
            }
            left_hand_data = {
                1: [0.0, math.radians(-20), math.radians(-30)],
                2: [0.0, math.radians(-25), math.radians(-35)],
                3: [0.0, math.radians(-20), math.radians(-25)],
                4: [0.0, math.radians(-15), math.radians(-20)],
                5: [0.0, math.radians(-10), math.radians(-15)]
            }
            positions_dict = {1: right_hand_data, 2: left_hand_data}
            success = hand.move_joints_pos(positions_dict, speed=0.5)
            print(f"Dual-hand dict-format set result: {'succeeded' if success else 'failed'}")
            if success:
                time.sleep(2)
                print(f"Current positions: {hand.get_joint_positions()}")

            print("\n--- Test dual-hand homing ---")
            success = hand.hand_zero()
            print(f"Dual-hand homing result: {'succeeded' if success else 'failed'}")
            time.sleep(3)

            return True
        else:
            print("PantheonHand20 dual-hand mode connection failed")
            return False

    except Exception as e:
        print(f"PantheonHand20 dual-hand mode test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        if hand and hand.is_connected():
            print("Homing...")
            hand.hand_zero()
            time.sleep(1)
            print("Disabling all joints...")
            disable_success = hand.enable_all_motors(False)
            print(f"Disable result: {'succeeded' if disable_success else 'failed'}")
            print("Closing dual-hand connection...")
            hand.close()
            print("Dual-hand connection closed")


def test_pantheonhand20_individual_control(can_config=None):
    """
    Test PantheonHand20 single joint / finger control.

    Args:
        can_config: Optional CAN config dict
    """
    print("\n=== Test PantheonHand20 single joint control ===")

    hand = None
    try:
        hand = create_hand("pantheonhand20", "right", can_config=can_config or {})

        if hand.connect():
            print("PantheonHand20 connected, starting single joint control test")
            time.sleep(1)

            hand.enable_all_motors()
            time.sleep(2)

            print("\n--- Test control single finger ---")
            finger_positions = [0.0, math.radians(30), math.radians(45)]
            success = hand.control_single_finger(0, finger_positions)
            print(f"Control thumb result: {'succeeded' if success else 'failed'}")
            if success:
                time.sleep(1)
                print(f"Current positions: {hand.get_joint_positions()}")

            print("\n--- Test control single joint ---")
            success = hand.control_finger_joint(1, 0, math.radians(20))
            print(f"Control index joint 1 result: {'succeeded' if success else 'failed'}")
            if success:
                time.sleep(1)
                print(f"Current positions: {hand.get_joint_positions()}")

            print("\n--- Test control multiple fingers ---")
            finger_positions_dict = {
                0: [0.0, math.radians(15), math.radians(25)],
                1: [0.0, math.radians(20), math.radians(30)],
                2: [0.0, math.radians(15), math.radians(20)]
            }
            success = hand.control_multiple_fingers(finger_positions_dict)
            print(f"Control multiple fingers result: {'succeeded' if success else 'failed'}")

            print("\n--- Test homing ---")
            success = hand.hand_zero()
            print(f"Homing result: {'succeeded' if success else 'failed'}")

            return True
        else:
            print("PantheonHand20 connection failed")
            return False

    except Exception as e:
        print(f"PantheonHand20 single joint control test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        if hand and hand.is_connected():
            print("Homing...")
            hand.hand_zero()
            time.sleep(1)
            print("Disabling all joints...")
            disable_success = hand.enable_all_motors(False)
            print(f"Disable result: {'succeeded' if disable_success else 'failed'}")
            hand.close()


def test_pantheonhand20_motor_status(can_config=None):
    """
    Test PantheonHand20 motor status queries.

    Args:
        can_config: Optional CAN config dict
    """
    print("\n=== Test PantheonHand20 motor status query ===")

    hand = None
    try:
        hand = create_hand("pantheonhand20", "right", can_config=can_config or {})

        if hand.connect():
            print("PantheonHand20 connected, starting motor status query test")
            time.sleep(1)

            hand.enable_all_motors()
            time.sleep(2)

            print("\n--- Test get all motor status ---")
            all_status = hand.get_motor_status()
            print(f"All motor status: {all_status}")

            print("\n--- Test get specific motor status ---")
            for motor_id in range(5):
                try:
                    motor_status = hand.get_motor_status(motor_id)
                    print(f"Motor {motor_id} status: {motor_status}")
                except Exception as e:
                    print(f"Failed to get motor {motor_id} status: {e}")

            return True
        else:
            print("PantheonHand20 connection failed")
            return False

    except Exception as e:
        print(f"PantheonHand20 motor status query test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        if hand and hand.is_connected():
            print("Homing...")
            hand.hand_zero()
            time.sleep(1)
            print("Disabling all joints...")
            disable_success = hand.enable_all_motors(False)
            print(f"Disable result: {'succeeded' if disable_success else 'failed'}")
            hand.close()


def main():
    """
    Main test entry.

    Usage:
    1. Choose CAN configuration for your hardware (optional)
    2. Uncomment the desired test functions to run tests
    3. Dual-hand mode requires dual-hand hardware
    """
    print("Starting PantheonHand20 tests")
    print("=" * 60)

    # Configure logging
    # test_log_management()
    set_log_level('INFO')
    enable_all_logs()
    set_both_output()

    # Get CAN config (optional; adjust channel etc. for your hardware)
    can_config = get_default_can_config()

    # ==================== Single-hand mode tests ====================
    print("\n" + "=" * 60)
    print("PantheonHand20 single-hand mode tests")
    print("=" * 60)

    # Test connection
    # test_pantheonhand20_connection(can_config)

    # Test rope tightening
    # test_pantheonhand20_rope_tight(can_config)

    # Test get_joint_positions
    # test_pantheonhand20_get_joint_positions(can_config)

    # Test move_joints_pos (list format)
    # test_pantheonhand20_move_joints_pos_list(can_config)

    # Test move_joints_pos (dict format)
    test_pantheonhand20_move_joints_pos_dict(can_config)

    # Test single joint control
    # test_pantheonhand20_individual_control(can_config)

    # Test motor status query
    # test_pantheonhand20_motor_status(can_config)

    # ==================== Dual-hand mode tests ====================
    print("\n" + "=" * 60)
    print("PantheonHand20 dual-hand mode tests (requires dual-hand hardware)")
    print("=" * 60)

    # test_pantheonhand20_double_mode(can_config)

    print("\n" + "=" * 60)
    print("All PantheonHand20 tests complete")


if __name__ == "__main__":
    main()
