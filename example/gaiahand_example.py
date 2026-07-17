#!/usr/bin/env python3
"""
GaiaHand control example

⭐ Recommended: GaiaHand20 (16-joint version), currently the main maintained release
⚠️ GaiaHand15 (15-joint version) is no longer maintained; example code kept for backward compatibility only

Features:
- Test move_joints_pos for different hand types, including single-hand and dual-hand modes
- Automatic serial port detection
- Motor smoothing level configuration
- Joint position control (list and dict formats)
- Gesture execution and homing operations
- Error handling and resource cleanup
- Log management (enable_all_logs, disable_all_logs, set_log_level, set_console_only,
  set_file_only, set_both_output, show_log_status, log_controller; exercise via test_log_management())

Baud rate configuration:
- GaiaHand15: 230400 (standard configuration)
  - Note: some test functions in this file use 921600, but the standard setting is 230400
- GaiaHand20 without main board: 230400 (default configuration)
- GaiaHand20 with main board: 921600 (high-performance configuration)

Usage:
1. Choose an appropriate baud rate for your hardware
2. Uncomment the desired test functions in main() to run tests
3. GaiaHand20 tests are preferred by default
"""

import time
import sys
import os
import math

# Add project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from hand import create_hand, HandSide
from hand.gaiahand.hand_mappings import FingerType, JointType
from hand.utils.serial_utils import auto_detect_gaia_ports

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

def set_motor_smooth_level(hand, device_id: int = 255, level: int = 3, description: str = ""):
    """
    Helper to set motor smoothing level
    
    Args:
        hand: Hand control instance
        device_id: Device ID; 255 broadcasts to all motors, None uses the default
        level: Smoothing level (0-5); higher values yield smoother motion
        description: Optional description text for logging
    """
    desc_text = f" ({description})" if description else ""
    print(f"Setting motor smoothing level{desc_text}...")
    print(f"  Parameters: device_id={device_id}, level={level}")
    try:
        hand.config_pos_lpf_lv(device_id=device_id, level=level)
        print(f"Motor smoothing level set succeeded (device_id={device_id}, level={level})")
        return True
    except Exception as e:
        print(f"Failed to set motor smoothing level: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_log_management():
    """Test log management features"""
    print("\n" + "=" * 60)
    print("=== Test log management ===")

    # 1. Test enabling all logs
    print("\n1. Enable all logs...")
    enable_all_logs()
    print("All logs enabled")

    # 2. Test setting log level
    print("\n2. Set log level to DEBUG...")
    set_log_level('DEBUG')
    print("Log level set to DEBUG")

    # 3. Test different output modes
    print("\n3. Test different output modes...")

    print("   - Set to console output...")
    set_console_only()
    print("   Console-only output enabled")

    print("   - Set to file output...")
    set_file_only()
    print("   File-only output enabled")

    print("   - Set to console + file output...")
    set_both_output()
    print("   Console + file output enabled")

    # 4. Test disabling all logs
    print("\n4. Test disabling all logs...")
    disable_all_logs()
    print("All logs disabled")

    # Verify effect after disabling logs — messages below should not appear
    print("\n   Test effect after disabling logs (messages below should not appear):")
    from hand.core import get_logger
    test_logger = get_logger('test.disable_logs')
    test_logger.info("This INFO log should not appear")
    test_logger.warning("This WARNING log should not appear")
    test_logger.error("This ERROR log should not appear")
    print("   Disable-log test complete")

    # 5. Test per-script log control
    print("\n5. Test per-script log control...")
    log_controller.set_script_logging('gaiahand.motor', enabled=True, level='WARNING')
    print("Set gaiahand.motor to WARNING level")

    # 6. Show current log status
    print("\n6. Current log status:")
    show_log_status()

    # 7. Re-enable logs for subsequent tests
    print("\n7. Re-enable logs for subsequent tests...")
    enable_all_logs()
    set_log_level('INFO')
    set_both_output()
    print("Logs re-enabled")


def detect_serial_ports():
    """
    Detect available serial ports
    
    Returns:
        dict: Serial port configuration dict
    """
    try:
        print("Detecting available serial ports...")
        ports_config = auto_detect_gaia_ports()
        
        if not ports_config or not ports_config['available']:
            print("No serial ports detected; check hardware connection")
            return None
        
        return ports_config
        
    except Exception as e:
        print(f"Serial port detection failed: {e}")
        return None


def test_gaiahand20_create_hand(ports_config):
    """
    Test GaiaHand20 instance creation
    
    Lists concrete ways to create a hand (single/dual, serial/SLCAN, with/without main board, etc.).
    """
    print("\n" + "=" * 60)
    print("=== GaiaHand20 creation and status query examples ===")
    print("=" * 60)
    
    # ==================== 1. Ways to create a hand ====================
    print("\n[1. Ways to create GaiaHand20]\n")
    print("Serial ports: Windows uses COM4/COM5 etc.; Linux uses /dev/ttyUSB0, /dev/ttyACM0, etc.")
    print("Recommended: use ports_config = auto_detect_gaia_ports() for auto-detection, port=ports_config['right']\n")
    
    print("1. Right hand only - serial direct (no main board, baudrate 230400)")
    print("   # Use ports_config (recommended):")
    print("   hand = create_hand('gaiahand20', 'right', port=ports_config['right'], baudrate=230400)")
    print("   # Or specify port: Windows port='COM4', Linux port='/dev/ttyUSB0'")
    print()
    
    print("2. Right hand only - serial direct (with main board, baudrate 921600)")
    print("   hand = create_hand('gaiahand20', 'right', port=ports_config['right'], baudrate=921600, has_main_board=True)")
    print("   # Or specify: port='COM4' (Win) / port='/dev/ttyUSB0' (Linux)")
    print()
    
    print("3. Right hand only - SLCAN/CAN mode (main board by default)")
    print("   hand = create_hand('gaiahand20', 'right', port=ports_config['right'], use_slcan=True)")
    print("   # Or specify: port='COM6' (Win) / port='/dev/ttyUSB0' (Linux)")
    print("   # Optional: slcan_tty_baudrate=115200, slcan_arbitration_bitrate=1000000, slcan_data_bitrate=2000000")
    print()
    
    print("4. Left hand only - serial direct")
    print("   hand = create_hand('gaiahand20', 'left', port=ports_config['left'], baudrate=230400)")
    print("   # Or specify: port='COM5' (Win) / port='/dev/ttyUSB1' (Linux)")
    print()
    
    print("5. Dual-hand mode - serial direct")
    print("   hand = create_hand('gaiahand20', 'double', left_port=ports_config['left'], right_port=ports_config['right'], baudrate=230400)")
    print("   # Or specify: left_port='COM5', right_port='COM4' (Win) / left_port='/dev/ttyUSB1', right_port='/dev/ttyUSB0' (Linux)")
    print("   # With main board: baudrate=921600")
    print()
    
    print("6. Dual-hand mode - SLCAN/CAN (main board by default)")
    print("   hand = create_hand('gaiahand20', 'double', left_port=ports_config['left'], right_port=ports_config['right'], use_slcan=True)")
    print("   # Or specify: left_port='COM5', right_port='COM4' (Win) / left_port='/dev/ttyUSB1', right_port='/dev/ttyUSB0' (Linux)")
    print()


def test_gaiahand20_get_status(ports_config):
    """
    Test GaiaHand20 status queries
    
    Demonstrates connection state, joint positions, single-motor status, and all-motor status.
    """
    print("\n" + "=" * 60)
    print("=== GaiaHand20 status query test ===")
    print("=" * 60)
    
    if not ports_config or not ports_config.get('right'):
        print("Right-hand serial port not detected; skipping status test")
        return
    
    hand = None
    try:
        hand = create_hand("gaiahand20", "right", port=ports_config['right'], baudrate=230400)
        
        print(f"Instance created: hand_type={hand.hand_type.value}, hand_side={hand.hand_side_name}")
        print(f"Before connect is_connected(): {hand.is_connected()}")
        
        if not hand.connect():
            print("Connection failed; check serial port and hardware")
            return
        
        print(f"Connected (serial port: {ports_config['right']})")
        print(f"After connect is_connected(): {hand.is_connected()}")
        
        # Enable motors
        hand.enable_all_motors_broadcast(True)
        time.sleep(0.3)
        
        # 1. Get joint positions (async)
        print("\n--- 1. Joint positions (async) ---")
        positions = hand.get_joint_positions(sync=False)
        if positions:
            print(f"{len(positions)} joints total")
            print(f"  First 5 (rad): {[f'{p:.3f}' if p is not None else 'None' for p in positions[:5]]}")
            print(f"  First 5 (deg):   {[f'{math.degrees(p):.1f}°' if p is not None else 'None' for p in positions[:5]]}")
        
        # 2. Get joint positions (sync)
        print("\n--- 2. Joint positions (sync) ---")
        positions_sync = hand.get_joint_positions(sync=True, timeout=0.1)
        if positions_sync:
            print(f"{len(positions_sync)} joints total")
            print(f"  First 5 (deg): {[f'{math.degrees(p):.1f}°' if p is not None else 'None' for p in positions_sync[:5]]}")
        
        # 3. Get single motor status
        print("\n--- 3. Single motor status (motor 1) ---")
        status_1 = hand.get_motor_status(motor_id=1, sync=True, timeout=0.5)
        print(f"online={status_1.get('online')}, angle={status_1.get('angle')}°, fsm_state={status_1.get('fsm_state')}, "
              f"temp={status_1.get('temp')}°C, bus_voltage={status_1.get('bus_voltage')}V")
        
        # 4. Get all motor status (online/offline)
        print("\n--- 4. All motor status (online/offline) ---")
        all_status = hand.get_motor_status(motor_id=None, sync=True, timeout=2.0)
        if isinstance(all_status, dict) and 1 in all_status:
            v = all_status[1]
            if isinstance(v, dict):
                online_count = sum(1 for s in all_status.values() if isinstance(s, dict) and s.get('online'))
            else:
                online_count = sum(1 for s in all_status.values() if s)
            print(f"{len(all_status)} motors total, {online_count} online")
        
        hand.enable_all_motors_broadcast(False)
        hand.close()
        print("\nStatus query test complete")
            
    except Exception as e:
        print(f"Status query error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if hand and hasattr(hand, 'close'):
            try:
                hand.close()
            except Exception:
                pass


def test_gaiahand20_joint_limits(ports_config, connect_for_motion: bool = False):
    """
    Test GaiaHand20 joint limit APIs.

    By default only demonstrates limit table queries, enable/disable, temporary settings, and restore-default; no hardware connection or motion commands.
    Pass connect_for_motion=True to verify real clamping behavior on out-of-limit commands.

    All joint limit values are in radians (rad).
    """
    print("\n" + "=" * 60)
    print("=== GaiaHand20 joint limit API example ===")
    print("=" * 60)

    if not ports_config or not ports_config.get('right'):
        print("Right-hand serial port not detected; can still create object with example port and demo offline APIs")

    port = ports_config.get('right') if ports_config else None
    port = port or "COM0"
    hand = None

    try:
        # joint_limit_enabled defaults to True; shown explicitly here for clarity.
        hand = create_hand(
            "gaiahand20",
            "right",
            port=port,
            baudrate=230400,
            joint_limit_enabled=True,
        )

        print(f"Instance created: hand_type={hand.hand_type.value}, hand_side={hand.hand_side_name}")
        print(f"HandSDK joint limit default state: {hand.is_joint_limit_enabled()}")

        # 1. Query a single joint limit
        print("\n--- 1. Query single joint limit ---")
        thumb_j1_limit = hand.get_joint_limit(FingerType.THUMB, JointType.JOINT_1)
        print(f"Right thumb JOINT1 limit (rad): {thumb_j1_limit}")
        if thumb_j1_limit:
            print(
                "Right thumb JOINT1 limit (deg): "
                f"({math.degrees(thumb_j1_limit[0]):.1f}, {math.degrees(thumb_j1_limit[1]):.1f})"
            )

        # 2. Query the full active limit table
        print("\n--- 2. Query active limit table ---")
        limits = hand.get_joint_limits()
        print(f"Finger list: {list(limits.keys())}")
        print(f"thumb: {limits.get('thumb')}")

        # 3. Enable/disable HandSDK joint limits
        print("\n--- 3. Enable/disable HandSDK joint limits ---")
        hand.disable_joint_limit()
        print(f"After disable: {hand.is_joint_limit_enabled()}")
        hand.enable_joint_limit()
        print(f"After re-enable: {hand.is_joint_limit_enabled()}")

        # 4. Temporarily set a single joint limit
        print("\n--- 4. Temporarily set single joint limit ---")
        original_limit = hand.get_joint_limit(FingerType.THUMB, JointType.JOINT_1)
        hand.set_joint_limit(FingerType.THUMB, JointType.JOINT_1, -0.1, 0.1)
        print(f"After temp set thumb JOINT1: {hand.get_joint_limit(FingerType.THUMB, JointType.JOINT_1)}")
        hand.reset_joint_limits(FingerType.THUMB, JointType.JOINT_1)
        print(f"After restore single joint default thumb JOINT1: {hand.get_joint_limit(FingerType.THUMB, JointType.JOINT_1)}")
        print(f"Original default: {original_limit}")

        # 5. Temporarily batch-set limits; supports both string JOINT1 and JointType enum keys
        print("\n--- 5. Temporarily batch-set joint limits ---")
        hand.set_joint_limits({
            "thumb": {
                "JOINT1": (-0.2, 0.2),
                JointType.JOINT_2: (-0.3, 0.3),
            },
            FingerType.INDEX: {
                "JOINT1": (-0.15, 0.15),
            },
        })
        print(f"After batch set thumb: {hand.get_joint_limits().get('thumb')}")
        print(f"After batch set index JOINT1: {hand.get_joint_limit(FingerType.INDEX, JointType.JOINT_1)}")
        hand.reset_joint_limits()
        print(f"After restore all defaults thumb: {hand.get_joint_limits().get('thumb')}")

        # 6. Modify all joint limits at once
        print("\n--- 6. Modify all joint limits at once ---")
        default_limits = hand.get_joint_limits()
        all_joint_limits = {}
        for finger, joints in default_limits.items():
            all_joint_limits[finger] = {}
            for joint, (lower, upper) in joints.items():
                # Example: narrow each joint's temporary limit to the intersection of its default range and [-0.25, 0.25].
                # In production, replace this with a full limit table from calibration or config files.
                new_lower = max(lower, -0.25)
                new_upper = min(upper, 0.25)
                all_joint_limits[finger][joint] = (new_lower, new_upper)

        hand.set_joint_limits(all_joint_limits)
        total_joint_count = sum(len(joints) for joints in all_joint_limits.values())
        print(f"Temporarily modified {total_joint_count} joint limits at once")
        print(f"After full-table set thumb: {hand.get_joint_limits().get('thumb')}")
        print(f"After full-table set little: {hand.get_joint_limits().get('little')}")
        hand.reset_joint_limits()
        print(f"After full-table restore thumb: {hand.get_joint_limits().get('thumb')}")

        # 7. Disable limits at creation time
        print("\n--- 7. Disable joint limits at creation ---")
        hand_no_limit = create_hand(
            "gaiahand20",
            "right",
            port=port,
            baudrate=230400,
            joint_limit_enabled=False,
        )
        print(f"State after create with joint_limit_enabled=False: {hand_no_limit.is_joint_limit_enabled()}")
        if hasattr(hand_no_limit, 'close'):
            hand_no_limit.close()

        # 8. Optional: connect hardware to verify limit clamping
        print("\n--- 8. Optional: connect hardware to verify limit clamping ---")
        if not connect_for_motion:
            print("Skipping real motion by default. Call test_gaiahand20_joint_limits(ports_config, connect_for_motion=True) when needed")
            return

        print("Preparing to connect hardware and run an out-of-limit command example...")
        if not hand.connect():
            print("Connection failed; skipping real motion example")
            return

        hand.enable_all_motors_broadcast(True)
        time.sleep(0.5)
        hand.set_joint_limit(FingerType.THUMB, JointType.JOINT_1, -0.1, 0.1)
        print("Sending thumb JOINT1 = 1.0 rad; HandSDK will clamp to 0.1 rad and record a warning")
        hand.set_joint_angle(FingerType.THUMB, JointType.JOINT_1, 1.0, speed=0.3)
        time.sleep(1.0)
        hand.reset_joint_limits()
        hand.hand_zero()
        time.sleep(1.0)

    except Exception as e:
        print(f"GaiaHand20 joint limit example failed: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if hand and hasattr(hand, 'is_connected') and hand.is_connected():
            try:
                hand.enable_all_motors_broadcast(False)
                hand.close()
            except Exception:
                pass


def test_gaiahand20_get_joint_positions(ports_config, tests_to_run=None):
    """
    Test GaiaHand20 get_joint_positions (16-joint version)
    
    ⭐ Recommended: GaiaHand20 is the currently maintained version
    
    Baud rate: 230400 (without main board)
    
    Args:
        ports_config: Serial port configuration dict
        tests_to_run: List of sub-tests to run, e.g. [1, 2, 3] runs tests 1, 2, and 3 only
                     If None or empty, run all tests (default behavior)
                     Available test IDs: 1-7
                     Test 1: get all joint positions (async)
                     Test 2: get all joint positions (sync)
                     Test 3: verify positions after setting
                     Test 4: repeated position reads (observe changes)
                     Test 5: get specific joint positions
                     Test 6: get positions after homing
                     Test 7: interpolate from zero to target, read position each step
    """
    print("\n=== Test GaiaHand20 get_joint_positions (16-joint version) ===")
    
    # If no test list is given, run all tests
    if tests_to_run is None:
        tests_to_run = [7]
    elif not tests_to_run:
        tests_to_run = [1, 2, 3, 4, 5, 6, 7]
    
    # Show which tests will run
    print(f"Tests to run: {tests_to_run}")
    
    if not ports_config or not ports_config['right']:
        print("No available right-hand serial port; skipping get-position test")
        return
    
    hand = None
    try:
        # Create right-hand GaiaHand20 instance
        # ⭐ Baud rate configuration:
        # - With main board: baudrate=921600 (high-performance)
        # - Without main board: baudrate=230400 (default)
        # hand = create_hand("gaiahand20", "right", port=ports_config['right'], baudrate=921600, has_main_board=True)  # with main board, auto-detected port
        # hand = create_hand("gaiahand20", "right", port=ports_config['right'], baudrate=230400)  # without main board, auto-detected port
        # hand = create_hand("gaiahand20", "right", port='COM12', baudrate=921600, has_main_board=True)  # serial, user-specified port
        # hand = create_hand("gaiahand20", "right", port='COM8', baudrate=921600, has_main_board=True)  # serial, user-specified port, with main board

        # hand = create_hand("gaiahand20", "right", port=ports_config['right'], use_slcan=True)   # SLCAN mode, main board by default
        hand = create_hand("gaiahand20", "right", port='COM6', use_slcan=True, has_main_board=True)   # SLCAN mode, with main board


        if hand.connect():
            print(f"GaiaHand20 Connected (serial port: {ports_config['right']})")
            
            # Set motor smoothing (device_id=255 broadcasts to all motors, level=3)
            # Set motor smoothing (device_id=255 broadcasts to all motors, level=0)
            # Smoothing range 0-5; level=0 disables smoothing
            set_motor_smooth_level(hand, device_id=255, level=3, description="disable smoothing test")
            
            # Wait for settings to take effect
            # time.sleep(0.5)
            
            # Enable all joints
            print("Enabling all joints...")
            enable_success = hand.enable_all_motors_broadcast(True)
            print(f"Enable result: {'succeeded' if enable_success else 'failed'}")
            
            if not enable_success:
                print("Enable failed; cannot continue test")
                return
            
            # Wait for enable to stabilize
            time.sleep(0.5)
            
            # Test 1: get all joint positions (async); async mode recommended
            if 1 in tests_to_run:
                print("\n--- Test 1: get all joint positions (async) ---")
                all_positions = hand.get_joint_positions(sync=False)
                print(f"All joint positions (async): {all_positions}")
                print(f"Position data type: {type(all_positions)}")
                if isinstance(all_positions, (list, tuple)):
                    print(f"Position data length: {len(all_positions)}")
                    if len(all_positions) > 0:
                        print(f"First 5 joint positions: {all_positions[:5]}")
                        print(f"Last 5 joint positions: {all_positions[-5:]}")
                time.sleep(1)
            
            # Test 2: get all joint positions (sync)
            if 2 in tests_to_run:
                print("\n--- Test 2: get all joint positions (sync) ---")
                all_positions_sync = hand.get_joint_positions(sync=True, timeout=0.1)
                print(f"All joint positions (sync): {all_positions_sync}")
                print(f"Position data type: {type(all_positions_sync)}")
                if isinstance(all_positions_sync, (list, tuple)):
                    print(f"Position data length: {len(all_positions_sync)}")
                    if len(all_positions_sync) > 0:
                        print(f"First 5 joint positions: {all_positions_sync[:5]}")
                        print(f"Last 5 joint positions: {all_positions_sync[-5:]}")
                        # Convert to degrees for display
                        print("First 5 joint positions (deg): ", [math.degrees(p) if p is not None else None for p in all_positions_sync[:5]])
                time.sleep(0.5)
            
            # Test 3: verify positions after setting
            if 3 in tests_to_run:
                print("\n--- Test 3: verify positions after set ---")
                # Set a known target position
                target_positions = [
                    # Thumb 4 joints
                    0.0, math.radians(10.0), math.radians(20.0), math.radians(15.0),
                    # Index 3 joints
                    0.0, math.radians(45.0), math.radians(40.0),
                    # Middle 3 joints
                    0.0, math.radians(45.0), math.radians(45.0),
                    # Ring 3 joints
                    0.0, math.radians(40.0), math.radians(40.0),
                    # Little 3 joints
                    0.0, math.radians(45.0), math.radians(45.0)
                ]
                
                print(f"Target positions (rad): {target_positions[:5]}...")
                success = hand.move_joints_pos(target_positions, speed=0.8, use_broadcast=True)
                print(f"Set position result: {'succeeded' if success else 'failed'}")
                
                # Wait for motion to finish
                time.sleep(2)
                
                # Read current positions
                current_positions = hand.get_joint_positions(sync=True, timeout=0.1)
                print(f"Current positions (rad): {current_positions}")
                if isinstance(current_positions, (list, tuple)) and len(current_positions) >= 16:
                    print("Position comparison (first 5 joints):")
                    for i in range(5):
                        target = target_positions[i] if i < len(target_positions) else None
                        current = current_positions[i] if i < len(current_positions) else None
                        if target is not None and current is not None:
                            diff = abs(target - current)
                            print(f"  Joint {i+1}: target={math.degrees(target):.2f}°, current={math.degrees(current):.2f}°, error={math.degrees(diff):.2f}°")
                        else:
                            print(f"  Joint {i+1}: target={target}, current={current}")
                time.sleep(1)
            
            # Test 4: repeated position reads (observe changes)
            if 4 in tests_to_run:
                print("\n--- Test 4: repeated position reads (observe changes) ---")
                for i in range(3):
                    positions = hand.get_joint_positions(sync=True, timeout=0.1)
                    if isinstance(positions, (list, tuple)) and len(positions) >= 16:
                        # Show thumb 4 joints
                        thumb_positions = positions[:4] if len(positions) >= 4 else []
                        thumb_degrees = [math.degrees(p) if p is not None else None for p in thumb_positions]
                        print(f"Read {i+1} - thumb joint positions (deg): {thumb_degrees}")
                    else:
                        print(f"Read {i+1}: {positions}")
                    time.sleep(0.5)
            
            # Test 5: get specific joint positions (if supported)
            if 5 in tests_to_run:
                print("\n--- Test 5: get specific joint positions ---")
                # Note: joint_names usage may need adjustment per actual implementation
                # First fetch all positions, then extract specific joints
                all_positions = hand.get_joint_positions(sync=True, timeout=0.1)
                if isinstance(all_positions, (list, tuple)) and len(all_positions) >= 16:
                    # Extract thumb 4 joints (indices 0-3)
                    thumb_joints = all_positions[:4]
                    thumb_degrees = [math.degrees(p) if p is not None else None for p in thumb_joints]
                    print(f"Thumb 4 joint positions (deg): {thumb_degrees}")
                    
                    # Extract index 3 joints (indices 4-6)
                    index_joints = all_positions[4:7] if len(all_positions) >= 7 else []
                    index_degrees = [math.degrees(p) if p is not None else None for p in index_joints]
                    print(f"Index 3 joint positions (deg): {index_degrees}")
                    
                    # Extract middle 3 joints (indices 7-9)
                    middle_joints = all_positions[7:10] if len(all_positions) >= 10 else []
                    middle_degrees = [math.degrees(p) if p is not None else None for p in middle_joints]
                    print(f"Middle 3 joint positions (deg): {middle_degrees}")
            
            # Run homing if test 6 is scheduled, or if test 3 ran (test 3 changes positions)
            # If only test 6 runs, homing is still required first
            if 6 in tests_to_run or (3 in tests_to_run):
                print("\nExecuting homing...")
                success = hand.hand_zero()
                print(f"Homing result: {'succeeded' if success else 'failed'}")
                time.sleep(1)
            
            # Test 6: get positions after homing
            if 6 in tests_to_run:
                print("\n--- Test 6: get positions after homing ---")
                zero_positions = hand.get_joint_positions(sync=True, timeout=0.1)
                print(f"Positions after homing (rad): {zero_positions}")
                if isinstance(zero_positions, (list, tuple)) and len(zero_positions) >= 16:
                    zero_degrees = [math.degrees(p) if p is not None else None for p in zero_positions]
                    print(f"Positions after homing (deg): {zero_degrees}")
            
            # Test 7: interpolate from zero to target, read position each step
            if 7 in tests_to_run:
                print("\n--- Test 7: interpolate from zero to target, read each step ---")
                # Target positions (same as test 3)
                target_positions = [
                    # Thumb 4 joints
                    0.0, math.radians(10.0), math.radians(20.0), math.radians(15.0),
                    # Index 3 joints
                    0.0, math.radians(30.0), math.radians(40.0),
                    # Middle 3 joints
                    0.0, math.radians(25.0), math.radians(35.0),
                    # Ring 3 joints
                    0.0, math.radians(20.0), math.radians(30.0),
                    # Little 3 joints
                    0.0, math.radians(15.0), math.radians(25.0)
                ]
                
                # Home first to start from zero
                # print("Homing first to ensure start from zero...")
                # hand.hand_zero()
                # time.sleep(1)
                
                # Read initial positions (should be 0 or near 0) — async
                print("Getting initial positions asynchronously...")
                initial_positions = hand.get_joint_positions(sync=False)
                print(f"Initial positions (rad): {initial_positions[:5]}...")
                if isinstance(initial_positions, (list, tuple)) and len(initial_positions) >= 16:
                    initial_degrees = [math.degrees(p) if p is not None else None for p in initial_positions[:5]]
                    print(f"Initial positions (deg, first 5 joints): {initial_degrees}")
                
                # Interpolation parameters
                interpolation_steps = 100  # interpolation steps
                step_delay = 0.0  # delay per step (seconds)
                
                print(f"\nStarting interpolation: zero to target, {interpolation_steps} steps, {step_delay}s delay per step")
                print(f"Target positions (deg, first 5 joints): {[math.degrees(p) if p is not None else None for p in target_positions[:5]]}")
                
                # Run interpolation
                for step in range(interpolation_steps + 1):
                    # Compute interpolation factor t ∈ [0, 1]
                    t = step / interpolation_steps
                    
                    # Compute interpolated position for this step
                    interpolated_positions = []
                    for i in range(len(target_positions)):
                        if i < len(initial_positions) and initial_positions[i] is not None:
                            start_pos = initial_positions[i]
                            end_pos = target_positions[i]
                            interpolated_pos = start_pos + (end_pos - start_pos) * t
                            interpolated_positions.append(interpolated_pos)
                        else:
                            interpolated_positions.append(target_positions[i] * t)
                    
                    # Send interpolated position
                    success = hand.move_joints_pos(interpolated_positions, speed=0.8, use_broadcast=True)
                    if not success:
                        print(f"Warning: failed to set position at step {step}")
                    
                    # Read actual positions (async)
                    actual_positions = hand.get_joint_positions(sync=False)
                    
                    # # Show progress and position info
                    # if isinstance(actual_positions, (list, tuple)) and len(actual_positions) >= 16:
                    #     # Show first 5 joints target vs actual
                    #     print(f"\nStep {step}/{interpolation_steps} (progress: {t*100:.1f}%):")
                    #     print(f"  Target positions (deg, first 5 joints): {[math.degrees(p) if p is not None else None for p in interpolated_positions[:5]]}")
                    #     actual_degrees = [math.degrees(p) if p is not None else None for p in actual_positions[:5]]
                    #     print(f"  Actual positions (deg, first 5 joints): {actual_degrees}")
                        
                    #     # Compute error
                    #     errors = []
                    #     for i in range(min(5, len(interpolated_positions), len(actual_positions))):
                    #         if interpolated_positions[i] is not None and actual_positions[i] is not None:
                    #             error = abs(interpolated_positions[i] - actual_positions[i])
                    #             errors.append(math.degrees(error))
                    #         else:
                    #             errors.append(None)
                    #     print(f"  Position errors (deg, first 5 joints): {errors}")
                    # else:
                    #     print(f"Step {step}/{interpolation_steps}: failed to get positions or invalid data format")
                    
                    # Wait for motors to move
                    # if step < interpolation_steps:  # no delay on final step
                    #     time.sleep(step_delay)
                
                print("\nInterpolation complete!")
                
                # Final position read to confirm target reached (async)
                print("Getting final positions asynchronously...")
                final_positions = hand.get_joint_positions(sync=False)
                if isinstance(final_positions, (list, tuple)) and len(final_positions) >= 16:
                    final_degrees = [math.degrees(p) if p is not None else None for p in final_positions[:5]]
                    target_degrees = [math.degrees(p) if p is not None else None for p in target_positions[:5]]
                    print(f"\nFinal positions (deg, first 5 joints): {final_degrees}")
                    print(f"Target positions (deg, first 5 joints): {target_degrees}")
                    
                    # Compute final error
                    final_errors = []
                    for i in range(min(5, len(target_positions), len(final_positions))):
                        if target_positions[i] is not None and final_positions[i] is not None:
                            error = abs(target_positions[i] - final_positions[i])
                            final_errors.append(math.degrees(error))
                        else:
                            final_errors.append(None)
                    print(f"Final errors (deg, first 5 joints): {final_errors}")
                
                time.sleep(1)
                
                # hand.hand_zero()
                # time.sleep(1)
            
        else:
            print(f"GaiaHand20 connection failed (serial port: {ports_config['right']})")
            
    except Exception as e:
        print(f"GaiaHand20 get_joint_positions test failed: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if hand and hand.is_connected():
            print("Homing...")
            hand.hand_zero()
            time.sleep(1)
            print("Disabling all joints...")
            disable_success = hand.enable_all_motors_broadcast(False)
            print(f"Disable result: {'succeeded' if disable_success else 'failed'}")
            hand.close()


def test_gaiahand20_get_joints_pos_vel(ports_config, tests_to_run=None):
    """
    Test GaiaHand20Adapter.get_joints_pos_vel: joint position (rad) and angular velocity (rad/s); protocol dict keys match move_joints_pos.

    Single right hand: key 3 = full-hand position, 5 = full-hand velocity; dual-hand adds 4/6 for left hand.
    No-arg call returns full hand; FingerType + JointType returns that joint only (single-element list).

    Connection options align with test_gaiahand20_get_joint_positions (serial / SLCAN, baud rate, main board).

    Args:
        ports_config: Serial port configuration dict
        tests_to_run: Sub-test list. Default [7] (same tier as test 7 in test_gaiahand20_get_joint_positions: read while interpolating).
                     1 — full-hand read with no args; 2 — thumb first joint; 3 — full-hand read after motion, compare thumb;
                     7 — interpolate from current to target, get_joints_pos_vel each step for position (3) and velocity (5).
    """
    print("\n=== Test GaiaHand20 get_joints_pos_vel (position+velocity, protocol keys 3/5) ===")

    if tests_to_run is None:
        tests_to_run = [7]
    elif not tests_to_run:
        tests_to_run = [1, 2, 3, 7]

    print(f"Tests to run: {tests_to_run}")

    if not ports_config or not ports_config['right']:
        print("No available right-hand serial port; skipping get_joints_pos_vel test")
        return

    hand = None
    try:
        # Same as test_gaiahand20_get_joint_positions; adjust to your hardware:
        # hand = create_hand("gaiahand20", "right", port=ports_config['right'], baudrate=921600, has_main_board=True)
        # hand = create_hand("gaiahand20", "right", port=ports_config['right'], baudrate=230400)
        # hand = create_hand("gaiahand20", "right", port='COM6', use_slcan=True, has_main_board=True)
        # hand = create_hand("gaiahand20", "right", port=ports_config['right'], baudrate=230400)

        hand = create_hand("gaiahand20", "right", port='COM6', use_slcan=True, has_main_board=True)

        if not hasattr(hand, 'get_joints_pos_vel'):
            print("Current adapter does not implement get_joints_pos_vel; skipping")
            return

        if hand.connect():
            print(f"GaiaHand20 Connected (serial port: {ports_config['right']})")

            set_motor_smooth_level(hand, device_id=255, level=3, description="get_joints_pos_vel test")

            print("Enabling all joints...")
            enable_success = hand.enable_all_motors_broadcast(True)
            print(f"Enable result: {'succeeded' if enable_success else 'failed'}")
            if not enable_success:
                print("Enable failed; cannot continue test")
                return

            time.sleep(0.5)

            if 1 in tests_to_run:
                print("\n--- Test 1: full-hand get_joints_pos_vel() with no args ---")
                full = hand.get_joints_pos_vel()
                print(f"Top-level keys: {sorted(full.keys())}")
                for top_key in sorted(full.keys()):
                    side = {3: "right position (rad)", 4: "left position (rad)", 5: "right velocity (rad/s)", 6: "left velocity (rad/s)"}.get(
                        top_key, f"key {top_key}"
                    )
                    inner = full[top_key]
                    print(f"  [{top_key}] {side}, finger ids: {sorted(inner.keys())}")
                    if 1 in inner:
                        pos_thumb = inner[1]
                        deg = [math.degrees(v) if v is not None else None for v in pos_thumb]
                        print(f"      Thumb joints (raw values): {pos_thumb}")
                        if top_key in (3, 4):
                            print(f"      Thumb joints (deg): {deg}")

            if 2 in tests_to_run:
                # print("\n--- Test 2: thumb first joint FingerType.THUMB, JointType.JOINT_1 ---")
                # one = hand.get_joints_pos_vel(FingerType.THUMB, JointType.JOINT_1, timeout=0.2)
                # print(f"Return: {one}")
                # for k in sorted(one.keys()):
                #     label = "position (rad)" if k in (3, 4) else "velocity (rad/s)"
                #     print(f"  [{k}] {label}: {one[k]}")
                pass

            if 3 in tests_to_run:
                # print("\n--- Test 3: re-read full hand after small motion (observe thumb pos/vel change) ---")
                # before = hand.get_joints_pos_vel()
                # bump = [
                #     0.0,
                #     math.radians(12.0),
                #     math.radians(10.0),
                #     math.radians(8.0),
                #     0.0,
                #     math.radians(5.0),
                #     math.radians(5.0),
                #     0.0,
                #     math.radians(5.0),
                #     math.radians(5.0),
                #     0.0,
                #     math.radians(5.0),
                #     math.radians(5.0),
                #     0.0,
                #     math.radians(5.0),
                #     math.radians(5.0),
                # ]
                # hand.move_joints_pos(bump, speed=0.5, use_broadcast=True)
                # time.sleep(1.0)
                # after = hand.get_joints_pos_vel()
                # if 3 in before and 3 in after and 1 in before[3] and 1 in after[3]:
                #     print(f"Thumb position (rad) before: {before[3][1]}")
                #     print(f"Thumb position (rad) after: {after[3][1]}")
                # if 5 in before and 5 in after and 1 in before[5] and 1 in after[5]:
                #     print(f"Thumb velocity (rad/s) before: {before[5][1]}")
                #     print(f"Thumb velocity (rad/s) after: {after[5][1]}")
                pass

            if 7 in tests_to_run:
                print(
                    "\n--- Test 7: interpolation with get_joints_pos_vel each step (read angle and velocity while moving, aligned with get_joint_positions test 7) ---"
                )
                target_positions = [
                    0.0,
                    math.radians(10.0),
                    math.radians(20.0),
                    math.radians(15.0),
                    0.0,
                    math.radians(30.0),
                    math.radians(40.0),
                    0.0,
                    math.radians(25.0),
                    math.radians(35.0),
                    0.0,
                    math.radians(20.0),
                    math.radians(30.0),
                    0.0,
                    math.radians(15.0),
                    math.radians(25.0),
                ]
                print("Getting initial positions asynchronously (same as interpolation start)...")
                initial_positions = hand.get_joint_positions(sync=False)
                print(f"Initial positions (rad, first 5 joints): {initial_positions[:5] if isinstance(initial_positions, (list, tuple)) else initial_positions}...")
                if isinstance(initial_positions, (list, tuple)) and len(initial_positions) >= 16:
                    print(
                        f"Initial positions (deg, first 5 joints): {[math.degrees(p) if p is not None else None for p in initial_positions[:5]]}"
                    )

                interpolation_steps = 10
                step_delay = 0.0
                print(
                    f"\nStarting interpolation: current position -> target position, {interpolation_steps} steps, get_joints_pos_vel after each step, delay {step_delay}s between steps"
                )
                print(
                    f"Target positions (deg, first 5 joints): {[math.degrees(p) if p is not None else None for p in target_positions[:5]]}"
                )

                for step in range(interpolation_steps + 1):
                    t = step / interpolation_steps
                    interpolated_positions = []
                    for i in range(len(target_positions)):
                        if (
                            isinstance(initial_positions, (list, tuple))
                            and i < len(initial_positions)
                            and initial_positions[i] is not None
                        ):
                            start_pos = initial_positions[i]
                            end_pos = target_positions[i]
                            interpolated_positions.append(start_pos + (end_pos - start_pos) * t)
                        else:
                            interpolated_positions.append(target_positions[i] * t)

                    success = hand.move_joints_pos(interpolated_positions, speed=0.8, use_broadcast=True)
                    if not success:
                        print(f"Warning: failed to set position at step {step}")

                    pv = hand.get_joints_pos_vel(timeout=0.025)
                    if step % 10 == 0 or step == interpolation_steps:
                        print(f"\nStep {step}/{interpolation_steps} (progress {t * 100:.1f}%):")
                        if 3 in pv and 1 in pv[3]:
                            pos_deg = [math.degrees(x) if x is not None else None for x in pv[3][1]]
                            print(f"  Thumb position (deg, protocol key 3): {pos_deg}")
                        if 5 in pv and 1 in pv[5]:
                            vel_dps = [math.degrees(w) if w is not None else None for w in pv[5][1]]
                            print(f"  Thumb angular velocity (deg/s, protocol key 5, converted from rad/s): {vel_dps}")

                print("\nInterpolation complete. Final full-hand get_joints_pos_vel:")
                final_pv = hand.get_joints_pos_vel(timeout=0.1)
                if 3 in final_pv and 5 in final_pv and 1 in final_pv[3]:
                    fd = [math.degrees(x) if x is not None else None for x in final_pv[3][1]]
                    td = [math.degrees(p) if p is not None else None for p in target_positions[:4]]
                    print(f"  Thumb final position (deg): {fd}")
                    print(f"  Thumb target position (deg): {td}")
                time.sleep(1)

        else:
            print(f"GaiaHand20 connection failed (serial port: {ports_config['right']})")

    except Exception as e:
        print(f"GaiaHand20 get_joints_pos_vel test failed: {e}")
        import traceback

        traceback.print_exc()
    finally:
        if hand and hand.is_connected():
            print("Homing...")
            try:
                hand.hand_zero()
                time.sleep(1)
            except Exception:
                pass
            print("Disabling all joints...")
            disable_success = hand.enable_all_motors_broadcast(False)
            print(f"Disable result: {'succeeded' if disable_success else 'failed'}")
            hand.close()


def test_gaiahand20_move_joints_pos_list(ports_config):
    """
    Test GaiaHand20 move_joints_pos (list format, 16-joint version)
    
    ⭐ Recommended: GaiaHand20 is the currently maintained version
    
    Baud rate:
    - Without main board: 230400 (used by this function)
    - With main board: 921600 (high-performance; see test_gaiahand20_smooth_transition())
    """
    print("\n=== Test GaiaHand20 move_joints_pos (list format, 16-joint version) ===")
    
    if not ports_config or not ports_config['right']:
        print("No available right-hand serial port; skipping single-hand test")
        return
    
    hand = None
    try:
        # Create right-hand GaiaHand20 instance
        hand = create_hand("gaiahand20", "right", port=ports_config['right'], baudrate=230400)

        if hand.connect():
            print(f"GaiaHand20 Connected (serial port: {ports_config['right']})")
            
            # Set motor smoothing (device_id=255 broadcasts to all motors, level=3)
            # Smoothing range 0-5; higher is smoother
            set_motor_smooth_level(hand, device_id=255, level=3, description="post-connect init")
            
            # Wait for settings to take effect
            time.sleep(0.5)
            
            # Enable all joints
            print("Enabling all joints...")
            enable_success = hand.enable_all_motors_broadcast(True)
            print(f"Enable result: {'succeeded' if enable_success else 'failed'}")
            
            if not enable_success:
                print("Enable failed; cannot continue test")
                return
            
            # Wait for enable to stabilize
            time.sleep(1)
            
            # Test single-hand mode — 16 joint positions
            print("\n--- Test single-hand mode (16 joints) ---")
            
            # Build 16-joint position list: thumb 4 joints, others 3 each (radians)
            custom_positions_16 = [
                # Thumb 4 joints
                0.0, math.radians(10.0), math.radians(10.0), math.radians(10.0),
                # Index 3 joints
                0.0, math.radians(10.0), math.radians(10.0),
                # Middle 3 joints
                0.0, math.radians(13.0), math.radians(15.0),
                # Ring 3 joints
                0.0, math.radians(18.0), math.radians(10.0),
                # Little 3 joints
                0.0, math.radians(19.0), math.radians(10.0)
            ]
            
            print(f"Setting 16-joint position data: {custom_positions_16}")
            success = hand.move_joints_pos(custom_positions_16, speed=1, use_broadcast=True)
            print(f"16-joint position result: {'succeeded' if success else 'failed'}")
            
            # Wait 2 seconds
            time.sleep(1)
            
            # Test thumb-only motion (4 joints)
            print("\n--- Test thumb independent motion (4 joints) ---")
            
            thumb_positions = [
                # Thumb 4 joints (radians)
                math.radians(10.0), math.radians(30.0), math.radians(45.0), math.radians(25.0),
                # Other fingers held still
                0.0, 0.0, 0.0,  # Index
                0.0, 0.0, 0.0,  # Middle
                0.0, 0.0, 0.0,  # Ring
                0.0, 0.0, 0.0   # Little
            ]
            
            print("Executing thumb flex motion...")
            success = hand.move_joints_pos(thumb_positions, speed=0.8, use_broadcast=True)
            print(f"Thumb motion result: {'succeeded' if success else 'failed'}")
            
            time.sleep(1)
            
            # Homing
            print("Executing homing...")
            success = hand.hand_zero()
            print(f"Homing result: {'succeeded' if success else 'failed'}")
            time.sleep(1)
            
        else:
            print(f"GaiaHand20 connection failed (serial port: {ports_config['right']})")
            
    except Exception as e:
        print(f"GaiaHand20 test failed: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if hand and hand.is_connected():
            print("Homing...")
            hand.hand_zero()
            time.sleep(1)
            print("Disabling all joints...")
            disable_success = hand.enable_all_motors_broadcast(False)
            print(f"Disable result: {'succeeded' if disable_success else 'failed'}")
            hand.close()


def test_gaiahand20_move_joints_pos_dict(ports_config):
    """
    Test GaiaHand20 move_joints_pos (dict format, 16-joint version)
    
    ⭐ Recommended: GaiaHand20 is the currently maintained version
    
    Baud rate: 230400 (without main board)
    """
    print("\n=== Test GaiaHand20 move_joints_pos (dict format, 16-joint version) ===")
    
    if not ports_config or not ports_config['right']:
        print("No available right-hand serial port; skipping dict-format test")
        return
    
    hand = None
    try:
        # Create right-hand GaiaHand20 instance
        # ⭐ Baud rate: 230400 (without main board)
        # For main-board hardware, use baudrate=921600
        hand = create_hand("gaiahand20", "right", port=ports_config['right'], baudrate=230400)

        if hand.connect():
            print(f"GaiaHand20 Connected (serial port: {ports_config['right']})")
            
            # Set motor smoothing (device_id=255 broadcasts to all motors, level=3)
            # Smoothing range 0-5; higher is smoother
            set_motor_smooth_level(hand, device_id=255, level=3, description="post-connect init")
            
            # Wait for settings to take effect
            time.sleep(0.5)
            
            # Enable all joints
            print("Enabling all joints...")
            enable_success = hand.enable_all_motors_broadcast(True)
            print(f"Enable result: {'succeeded' if enable_success else 'failed'}")
            
            if not enable_success:
                print("Enable failed; cannot continue test")
                return
            
            # Wait for enable to stabilize
            time.sleep(1)
            
            # Test 1: set right-hand positions via dict (single-hand mode)
            print("\n--- Test 1: set right-hand positions in dict format (single-hand mode) ---")
            right_hand_data = {
                1: [0.0, math.radians(10.0), math.radians(10.0), math.radians(10.0)],  # Thumb (4 joints, radians)
                2: [0.0, math.radians(10.0), math.radians(10.0)],  # Index (3 joints, radians)
                3: [0.0, math.radians(13.0), math.radians(15.0)],  # Middle (3 joints, radians)
                4: [0.0, math.radians(18.0), math.radians(10.0)],  # Ring (3 joints, radians)
                5: [0.0, math.radians(19.0), math.radians(10.0)]   # Little (3 joints, radians)
            }
            
            positions_dict = {1: right_hand_data}  # 1 = right hand
            print(f"Setting right-hand position data (dict format, radians)")
            print(f"  Thumb: {right_hand_data[1]}")
            print(f"  Index: {right_hand_data[2]}")
            print(f"  Middle: {right_hand_data[3]}")
            print(f"  Ring: {right_hand_data[4]}")
            print(f"  Little: {right_hand_data[5]}")
            
            success = hand.move_joints_pos(positions_dict, speed=1, use_broadcast=True)
            print(f"Dict-format set result: {'succeeded' if success else 'failed'}")
            
            if success:
                time.sleep(1)
                # Read current positions to verify
                current_positions = hand.get_joint_positions()
                print(f"Current positions: {current_positions}")
            
            # Test 2: set thumb flex via dict
            print("\n--- Test 2: set thumb flex in dict format ---")
            thumb_bend_data = {
                1: [math.radians(10.0), math.radians(30.0), math.radians(45.0), math.radians(25.0)],  # Thumb flex (4 joints, radians)
                2: [0.0, 0.0, 0.0],  # Index held still
                3: [0.0, 0.0, 0.0],  # Middle held still
                4: [0.0, 0.0, 0.0],  # Ring held still
                5: [0.0, 0.0, 0.0]   # Little held still
            }
            
            positions_dict = {1: thumb_bend_data}
            print(f"Setting thumb flex (dict format, radians)")
            success = hand.move_joints_pos(positions_dict, speed=0.8, use_broadcast=True)
            print(f"Thumb flex set result: {'succeeded' if success else 'failed'}")
            
            time.sleep(1)
            
            # Test 3: homing via dict (all joints extended)
            print("\n--- Test 3: homing in dict format (all joints extended) ---")
            zero_data = {
                1: [0.0, 0.0, 0.0, 0.0],  # Thumb (4 joints)
                2: [0.0, 0.0, 0.0],  # Index (3 joints)
                3: [0.0, 0.0, 0.0],  # Middle (3 joints)
                4: [0.0, 0.0, 0.0],  # Ring (3 joints)
                5: [0.0, 0.0, 0.0]   # Little (3 joints)
            }
            
            positions_dict = {1: zero_data}
            print("Executing homing (dict format)...")
            success = hand.move_joints_pos(positions_dict, speed=1, use_broadcast=True)
            print(f"Homing result: {'succeeded' if success else 'failed'}")
            
            time.sleep(1)
            
            # Test 4: command-6 format (single joint control)
            print("\n--- Test 4: command-6 format (single joint control) ---")
            # Command 6 format: 6: [hand, finger, joint, position (rad)]
            # Right hand, thumb, joint 2, 30 deg (radians)
            command_6_data = [1, 1, 2, math.radians(30.0)]
            positions_dict = {6: command_6_data}
            
            print(f"Command 6 data: right hand(1), thumb(1), joint 2, angle {math.degrees(math.radians(30.0)):.1f} deg")
            success = hand.move_joints_pos(positions_dict, speed=0.8, use_broadcast=False)
            print(f"Command 6 set result: {'succeeded' if success else 'failed'}")
            
            time.sleep(1)

            # Homing
            print("Executing homing...")
            success = hand.hand_zero()
            print(f"Homing result: {'succeeded' if success else 'failed'}")
            time.sleep(1)
            
        else:
            print(f"GaiaHand20 connection failed (serial port: {ports_config['right']})")
            
    except Exception as e:
        print(f"GaiaHand20 dict-format test failed: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if hand and hand.is_connected():
            print("Homing...")
            hand.hand_zero()
            time.sleep(1)
            print("Disabling all joints...")
            disable_success = hand.enable_all_motors_broadcast(False)
            print(f"Disable result: {'succeeded' if disable_success else 'failed'}")
            hand.close()


def test_gaiahand20_double_move_joints_pos_dict(ports_config):
    """
    Test GaiaHand20 dual-hand move_joints_pos (dict format, 32 joints)
    
    ⭐ Recommended: GaiaHand20 is the currently maintained version
    
    Baud rate: 230400 (without main board)
    """
    print("\n=== Test GaiaHand20 dual-hand move_joints_pos (dict format, 32 joints) ===")
    
    if not ports_config or not ports_config['left'] or not ports_config['right']:
        print("No available left/right serial ports; skipping dual-hand dict-format test")
        return
    
    hand = None
    try:
        # Create dual-hand GaiaHand20 instance
        # ⭐ Baud rate: 230400 (without main board, default)
        # For main-board hardware, pass baudrate=921600 to create_hand
        hand = create_hand("gaiahand20", "double", left_port=ports_config['left'], right_port=ports_config['right'])
        
        if hand.connect():
            print(f"GaiaHand20 dual-hand connected (left: {ports_config['left']}, right: {ports_config['right']})")
            
            # Set motor smoothing (device_id=255 broadcasts to all motors, level=3)
            # Smoothing range 0-5; higher is smoother
            set_motor_smooth_level(hand, device_id=255, level=3, description="post-connect init")
            
            # Wait for settings to take effect
            time.sleep(0.5)
            
            # Enable all joints
            print("Enabling all joints...")
            enable_success = hand.enable_all_motors_broadcast(True)
            print(f"Enable result: {'succeeded' if enable_success else 'failed'}")
            
            if not enable_success:
                print("Enable failed; cannot continue test")
                return
            
            # Wait for enable to stabilize
            time.sleep(1)
            
            # Test 1: set dual-hand positions via dict
            print("\n--- Test 1: set dual-hand positions in dict format ---")
            right_hand_data = {
                1: [0.0, math.radians(20.0), math.radians(30.0), math.radians(15.0)],  # Thumb (4 joints, radians)
                2: [0.0, math.radians(40.0), math.radians(55.0)],  # Index (3 joints, radians)
                3: [0.0, math.radians(35.0), math.radians(45.0)],  # Middle (3 joints, radians)
                4: [0.0, math.radians(30.0), math.radians(40.0)],  # Ring (3 joints, radians)
                5: [0.0, math.radians(25.0), math.radians(35.0)]   # Little (3 joints, radians)
            }
            
            left_hand_data = {
                1: [0.0, math.radians(20.0), math.radians(30.0), math.radians(15.0)],  # Thumb (4 joints, radians)
                2: [0.0, math.radians(40.0), math.radians(55.0)],  # Index (3 joints, radians)
                3: [0.0, math.radians(35.0), math.radians(45.0)],  # Middle (3 joints, radians)
                4: [0.0, math.radians(30.0), math.radians(40.0)],  # Ring (3 joints, radians)
                5: [0.0, math.radians(25.0), math.radians(35.0)]   # Little (3 joints, radians)
            }
            
            positions_dict = {
                1: right_hand_data,  # 1 = right hand
                2: left_hand_data    # 2 = left hand
            }
            
            print(f"Setting dual-hand position data (dict format, radians)")
            print(f"  Right thumb: {right_hand_data[1]}")
            print(f"  Left thumb: {left_hand_data[1]}")
            
            success = hand.move_joints_pos(positions_dict, speed=0.5, use_broadcast=True)
            print(f"Dual-hand dict-format set result: {'succeeded' if success else 'failed'}")
            
            time.sleep(2)
            
            # Test 2: set different gestures via dict
            print("\n--- Test 2: set different gestures in dict format ---")
            # Right hand: thumb flex
            right_custom = {
                1: [math.radians(5.0), math.radians(25.0), math.radians(40.0), math.radians(20.0)],  # Thumb flex (4 joints, radians)
                2: [0.0, 0.0, 0.0],  # Index held still
                3: [0.0, 0.0, 0.0],  # Middle held still
                4: [0.0, 0.0, 0.0],  # Ring held still
                5: [0.0, 0.0, 0.0]   # Little held still
            }
            
            # Left hand: index flex
            left_custom = {
                1: [0.0, 0.0, 0.0, 0.0],  # Thumb held still
                2: [0.0, math.radians(45.0), math.radians(60.0)],  # Index flex (3 joints, radians)
                3: [0.0, 0.0, 0.0],  # Middle held still
                4: [0.0, 0.0, 0.0],  # Ring held still
                5: [0.0, 0.0, 0.0]   # Little held still
            }
            
            positions_dict = {
                1: right_custom,  # Right hand
                2: left_custom     # Left hand
            }
            
            print(f"Setting custom dual-hand positions: right thumb flex, left index flex (dict format, radians)")
            success = hand.move_joints_pos(positions_dict, speed=0.5, use_broadcast=True)
            print(f"Custom dual-hand position result: {'succeeded' if success else 'failed'}")
            
            time.sleep(2)
            
            # Test 3: homing via dict (dual-hand open)
            print("\n--- Test 3: homing in dict format (dual-hand open) ---")
            zero_data = {
                1: [0.0, 0.0, 0.0, 0.0],  # Thumb (4 joints)
                2: [0.0, 0.0, 0.0],  # Index (3 joints)
                3: [0.0, 0.0, 0.0],  # Middle (3 joints)
                4: [0.0, 0.0, 0.0],  # Ring (3 joints)
                5: [0.0, 0.0, 0.0]   # Little (3 joints)
            }
            
            positions_dict = {
                1: zero_data,  # Right hand
                2: zero_data   # Left hand
            }
            
            print("Executing dual-hand homing (dict format)...")
            success = hand.move_joints_pos(positions_dict, speed=0.5, use_broadcast=True)
            print(f"Dual-hand homing result: {'succeeded' if success else 'failed'}")
            
            time.sleep(2)
            
        else:
            print(f"GaiaHand20 dual-hand connection failed (left: {ports_config['left']}, right: {ports_config['right']})")
            
    except Exception as e:
        print(f"GaiaHand20 dual-hand dict-format test failed: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if hand and hand.is_connected():
            print("Homing...")
            hand.hand_zero()
            time.sleep(1)
            print("Disabling all joints...")
            disable_success = hand.enable_all_motors_broadcast(False)
            print(f"Disable result: {'succeeded' if disable_success else 'failed'}")
            hand.close()


def test_gaiahand20_smooth_transition(ports_config):
    """
    Test GaiaHand20 smooth transition (16-joint version)
    
    ⭐ Recommended: GaiaHand20 is the currently maintained version
    
    Baud rate: 921600 (with main board, high-performance)
    """
    print("\n=== Test GaiaHand20 smooth transition (16-joint version) ===")
    
    if not ports_config or not ports_config['right']:
        print("No available right-hand serial port; skipping smooth transition test")
        return
    
    hand = None
    try:
        # Create right-hand GaiaHand20 instance
        # ⭐ Baud rate: 921600 (with main board, high-performance)
        # Without main board, use baudrate=230400
        hand = create_hand("gaiahand20", "right", port=ports_config['right'], baudrate=921600)
        
        if hand.connect():
            print(f"GaiaHand20 connected, starting smooth transition test (serial port: {ports_config['right']})")
            
            # Set motor smoothing (device_id=255 broadcasts to all motors, level=3)
            # Smoothing range 0-5; higher is smoother
            set_motor_smooth_level(hand, device_id=255, level=3, description="post-connect init")
            
            # Wait for settings to take effect
            time.sleep(0.5)
            
            # Enable all joints
            print("Enabling all joints...")
            enable_success = hand.enable_all_motors_broadcast(True)
            print(f"Enable result: {'succeeded' if enable_success else 'failed'}")
            
            if not enable_success:
                print("Enable failed; cannot continue test")
                return
            
            # Wait for enable to stabilize
            time.sleep(1)
            
            # Define start and end positions (radians)
            start_positions_16 = [0.0] * 16
            end_positions_16 = [
                # Thumb 4 joints
                0.0, math.radians(20.0), math.radians(35.0), math.radians(18.0),
                # Index 3 joints
                0.0, math.radians(43.0), math.radians(56.0),
                # Middle 3 joints
                0.0, math.radians(33.0), math.radians(25.0),
                # Ring 3 joints
                0.0, math.radians(28.0), math.radians(18.0),
                # Little 3 joints
                0.0, math.radians(19.0), math.radians(26.0)
            ]
            
            print("Running smooth transition: extended to flexed")
            
            # Transition in 8 steps
            for i in range(9):
                t = i / 8.0
                positions = []
                for j in range(16):
                    pos = start_positions_16[j] + (end_positions_16[j] - start_positions_16[j]) * t
                    positions.append(pos)
                
                print(f"Step {i+1}/9: transition progress {t*100:.1f}%")
                hand.move_joints_pos(positions, speed=0.5, use_broadcast=True)
                time.sleep(0.1)
                current_positions = hand.get_joint_positions()
                print(f"Current joint positions: {current_positions}")

            print("Smooth transition complete")
            
            time.sleep(2)
            
            # Reverse transition: flexed to extended
            print("Running reverse transition: flexed to extended")
            
            for i in range(10):
                t = i / 10.0
                positions = []
                for j in range(16):
                    pos = end_positions_16[j] + (start_positions_16[j] - end_positions_16[j]) * t
                    positions.append(pos)
                
                print(f"Step {i+1}/10: transition progress {t*100:.1f}%")
                hand.move_joints_pos(positions, speed=0.5, use_broadcast=True)
                time.sleep(0.1)
                current_positions = hand.get_joint_positions()
                print(f"Current joint positions: {current_positions}")
            
            print("Reverse transition complete")

            time.sleep(2)
            
        else:
            print(f"GaiaHand20 connection failed (serial port: {ports_config['right']})")
            
    except Exception as e:
        print(f"GaiaHand20 smooth transition test failed: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if hand and hand.is_connected():
            print("Homing...")
            hand.hand_zero()
            time.sleep(1)
            print("Disabling all joints...")
            disable_success = hand.enable_all_motors_broadcast(False)
            print(f"Disable result: {'succeeded' if disable_success else 'failed'}")
            hand.close()


def test_gaiahand20_double_move_joints_pos(ports_config):
    """
    Test GaiaHand20 dual-hand move_joints_pos (32 joints)
    
    ⭐ Recommended: GaiaHand20 is the currently maintained version
    
    Baud rate: 230400 (without main board)
    """
    print("\n=== Test GaiaHand20 dual-hand move_joints_pos (32 joints) ===")
    
    if not ports_config or not ports_config['left'] or not ports_config['right']:
        print("No available left/right serial ports; skipping dual-hand test")
        return
    
    hand = None
    try:
        # Create dual-hand GaiaHand20 instance
        # ⭐ Baud rate: 230400 (without main board, default)
        # For main-board hardware, pass baudrate=921600 to create_hand
        hand = create_hand("gaiahand20", "double", left_port=ports_config['left'], right_port=ports_config['right'])
        
        if hand.connect():
            print(f"GaiaHand20 dual-hand connected (left: {ports_config['left']}, right: {ports_config['right']})")
            
            # Set motor smoothing (device_id=255 broadcasts to all motors, level=3)
            # Smoothing range 0-5; higher is smoother
            set_motor_smooth_level(hand, device_id=255, level=3, description="post-connect init")
            
            # Wait for settings to take effect
            time.sleep(0.5)
            
            # Enable all joints
            print("Enabling all joints...")
            enable_success = hand.enable_all_motors_broadcast(True)
            print(f"Enable result: {'succeeded' if enable_success else 'failed'}")
            
            if not enable_success:
                print("Enable failed; cannot continue test")
                return
            
            # Wait for enable to stabilize
            time.sleep(1)
            
            # Test dual-hand mode — 32 joint positions
            print("\n--- Test dual-hand mode (32 joints) ---")
            
            # Build 32-joint test positions (radians)
            right_positions_16 = [
                # Thumb 4 joints
                0.0, math.radians(20.0), math.radians(30.0), math.radians(15.0),
                # Other fingers
                0.0, math.radians(40.0), math.radians(55.0),  # Index
                0.0, math.radians(35.0), math.radians(45.0),  # Middle
                0.0, math.radians(30.0), math.radians(40.0),  # Ring
                0.0, math.radians(25.0), math.radians(35.0)   # Little
            ]
            left_positions_16 = [
                # Thumb 4 joints
                0.0, math.radians(20.0), math.radians(30.0), math.radians(15.0),
                # Other fingers
                0.0, math.radians(40.0), math.radians(55.0),  # Index
                0.0, math.radians(35.0), math.radians(45.0),  # Middle
                0.0, math.radians(30.0), math.radians(40.0),  # Ring
                0.0, math.radians(25.0), math.radians(35.0)   # Little
            ]
            double_positions_32 = right_positions_16 + left_positions_16
            
            print(f"Setting dual-hand 32-joint position data")
            
            # Use broadcast mode
            success = hand.move_joints_pos(double_positions_32, speed=0.5, use_broadcast=True)
            print(f"Dual-hand 32-joint broadcast result: {'succeeded' if success else 'failed'}")
            
            time.sleep(2)
            
            # Test dual-hand mode — custom positions
            print("\n--- Test dual-hand mode (custom positions) ---")
            
            # Right hand: thumb flex (radians)
            right_custom = [
                # Thumb 4 joints
                math.radians(5.0), math.radians(25.0), math.radians(40.0), math.radians(20.0),
                # Other fingers
                0.0, 0.0, 0.0,  # Index
                0.0, 0.0, 0.0,  # Middle
                0.0, 0.0, 0.0,  # Ring
                0.0, 0.0, 0.0   # Little
            ]
            
            # Left hand: index flex (radians)
            left_custom = [
                # Thumb 4 joints
                0.0, 0.0, 0.0, 0.0,
                # Index
                0.0, math.radians(45.0), math.radians(60.0),
                # Other fingers
                0.0, 0.0, 0.0,  # Middle
                0.0, 0.0, 0.0,  # Ring
                0.0, 0.0, 0.0   # Little
            ]
            
            custom_double_positions_32 = right_custom + left_custom
            print(f"Setting custom dual-hand 32-joint positions: right thumb flex, left index flex")
            success = hand.move_joints_pos(custom_double_positions_32, speed=0.5, use_broadcast=True)
            print(f"Custom dual-hand position result: {'succeeded' if success else 'failed'}")
            
            time.sleep(2)
            
            # Test dual-hand open gesture
            print("\n--- Test dual-hand open gesture (32 joints) ---")
            double_open_32 = [0.0] * 32
            print("Executing dual-hand open gesture...")
            success = hand.move_joints_pos(double_open_32, speed=0.5, use_broadcast=True)
            print(f"Dual-hand open result: {'succeeded' if success else 'failed'}")
            
            time.sleep(2)
            
        else:
            print(f"GaiaHand20 dual-hand connection failed (left: {ports_config['left']}, right: {ports_config['right']})")
            
    except Exception as e:
        print(f"GaiaHand20 dual-hand test failed: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if hand and hand.is_connected():
            print("Homing...")
            hand.hand_zero()
            time.sleep(1)
            print("Disabling all joints...")
            disable_success = hand.enable_all_motors_broadcast(False)
            print(f"Disable result: {'succeeded' if disable_success else 'failed'}")
            hand.close()



def test_gaiahand20_double_get_joint_positions(ports_config):
    """
    Test GaiaHand20 dual-hand get_joint_positions (32 joints)
    
    ⭐ Recommended: GaiaHand20 is the currently maintained version
    
    Baud rate: 230400 (without main board)
    """
    print("\n=== Test GaiaHand20 dual-hand get_joint_positions (32 joints) ===")
    
    if not ports_config or not ports_config['left'] or not ports_config['right']:
        print("No available left/right serial ports; skipping dual-hand get-position test")
        return
    
    hand = None
    try:
        # Create dual-hand GaiaHand20 instance
        # ⭐ Baud rate: 230400 (without main board, default)
        # For main-board hardware, pass baudrate=921600 to create_hand
        hand = create_hand("gaiahand20", "double", left_port=ports_config['left'], right_port=ports_config['right'])
        
        if hand.connect():
            print(f"GaiaHand20 dual-hand connected (left: {ports_config['left']}, right: {ports_config['right']})")
            
            # Set motor smoothing (device_id=255 broadcasts to all motors, level=3)
            # Smoothing range 0-5; higher is smoother
            set_motor_smooth_level(hand, device_id=255, level=3, description="post-connect init")
            
            # Wait for settings to take effect
            time.sleep(0.5)
            
            # Enable all joints
            print("Enabling all joints...")
            enable_success = hand.enable_all_motors_broadcast(True)
            print(f"Enable result: {'succeeded' if enable_success else 'failed'}")
            
            if not enable_success:
                print("Enable failed; cannot continue test")
                return
            
            # Wait for enable to stabilize
            time.sleep(1)
            
            # Test 1: get all dual-hand joint positions (async)
            print("\n--- Test 1: get all dual-hand joint positions (async) ---")
            all_positions = hand.get_joint_positions(sync=False)
            print(f"All dual-hand joint positions (async): {all_positions}")
            print(f"Position data type: {type(all_positions)}")
            if isinstance(all_positions, dict):
                print(f"Hand count: {len(all_positions)}")
                for hand_name, positions in all_positions.items():
                    print(f"  {hand_name} hand positions: {positions}")
                    if isinstance(positions, (list, tuple)):
                        print(f"  {hand_name} hand position count: {len(positions)}")
            time.sleep(0.5)
            
            # Test 2: get all dual-hand joint positions (sync)
            print("\n--- Test 2: get all dual-hand joint positions (sync) ---")
            all_positions_sync = hand.get_joint_positions(sync=True, timeout=0.1)
            print(f"All dual-hand joint positions (sync): {all_positions_sync}")
            print(f"Position data type: {type(all_positions_sync)}")
            if isinstance(all_positions_sync, dict):
                for hand_name, positions in all_positions_sync.items():
                    print(f"  {hand_name} hand positions: {positions}")
                    if isinstance(positions, (list, tuple)) and len(positions) >= 16:
                        # Convert to degrees for display
                        degrees = [math.degrees(p) if p is not None else None for p in positions[:5]]
                        print(f"  {hand_name} hand first 5 joint positions (deg): {degrees}")
            time.sleep(0.5)
            
            # Test 3: verify dual-hand positions after set
            print("\n--- Test 3: verify dual-hand positions after set ---")
            # Set right-hand positions
            right_positions = [
                # Thumb 4 joints
                0.0, math.radians(10.0), math.radians(20.0), math.radians(15.0),
                # Other fingers
                0.0, math.radians(30.0), math.radians(40.0),  # Index
                0.0, math.radians(25.0), math.radians(35.0),  # Middle
                0.0, math.radians(20.0), math.radians(30.0),  # Ring
                0.0, math.radians(15.0), math.radians(25.0)   # Little
            ]
            # Set left-hand positions
            left_positions = [
                # Thumb 4 joints
                0.0, math.radians(5.0), math.radians(15.0), math.radians(10.0),
                # Other fingers
                0.0, math.radians(25.0), math.radians(35.0),  # Index
                0.0, math.radians(20.0), math.radians(30.0),  # Middle
                0.0, math.radians(15.0), math.radians(25.0),  # Ring
                0.0, math.radians(10.0), math.radians(20.0)   # Little
            ]
            
            double_positions = right_positions + left_positions
            print(f"Target dual-hand positions (right first 5 joints, rad): {right_positions[:5]}")
            print(f"Target dual-hand positions (left first 5 joints, rad): {left_positions[:5]}")
            success = hand.move_joints_pos(double_positions, speed=0.8, use_broadcast=True)
            print(f"Dual-hand set position result: {'succeeded' if success else 'failed'}")
            
            # Wait for motion to finish
            time.sleep(2)
            
            # Read current positions
            current_positions = hand.get_joint_positions(sync=True, timeout=0.1)
            print(f"Current positions: {current_positions}")
            if isinstance(current_positions, dict):
                if 'right' in current_positions:
                    right_current = current_positions['right']
                    if isinstance(right_current, (list, tuple)) and len(right_current) >= 5:
                        print("Right-hand position comparison (first 5 joints):")
                        for i in range(5):
                            target = right_positions[i] if i < len(right_positions) else None
                            current = right_current[i] if i < len(right_current) else None
                            if target is not None and current is not None:
                                diff = abs(target - current)
                                print(f"  Joint {i+1}: target={math.degrees(target):.2f}°, current={math.degrees(current):.2f}°, error={math.degrees(diff):.2f}°")
                
                if 'left' in current_positions:
                    left_current = current_positions['left']
                    if isinstance(left_current, (list, tuple)) and len(left_current) >= 5:
                        print("Left-hand position comparison (first 5 joints):")
                        for i in range(5):
                            target = left_positions[i] if i < len(left_positions) else None
                            current = left_current[i] if i < len(left_current) else None
                            if target is not None and current is not None:
                                diff = abs(target - current)
                                print(f"  Joint {i+1}: target={math.degrees(target):.2f}°, current={math.degrees(current):.2f}°, error={math.degrees(diff):.2f}°")
            time.sleep(1)
            
            # Test 4: repeated dual-hand position reads
            print("\n--- Test 4: repeated dual-hand position reads ---")
            for i in range(3):
                positions = hand.get_joint_positions(sync=True, timeout=0.1)
                if isinstance(positions, dict):
                    if 'right' in positions:
                        right_pos = positions['right']
                        if isinstance(right_pos, (list, tuple)) and len(right_pos) >= 4:
                            thumb_degrees = [math.degrees(p) if p is not None else None for p in right_pos[:4]]
                            print(f"Read {i+1} - right thumb joint positions (deg): {thumb_degrees}")
                    if 'left' in positions:
                        left_pos = positions['left']
                        if isinstance(left_pos, (list, tuple)) and len(left_pos) >= 4:
                            thumb_degrees = [math.degrees(p) if p is not None else None for p in left_pos[:4]]
                            print(f"Read {i+1} - left thumb joint positions (deg): {thumb_degrees}")
                time.sleep(0.5)
            
            # Homing
            print("\nExecuting dual-hand homing...")
            success = hand.hand_zero()
            print(f"Homing result: {'succeeded' if success else 'failed'}")
            time.sleep(1)
            
            # Test 5: get dual-hand positions after homing
            print("\n--- Test 5: get dual-hand positions after homing ---")
            zero_positions = hand.get_joint_positions(sync=True, timeout=0.1)
            print(f"Positions after homing: {zero_positions}")
            if isinstance(zero_positions, dict):
                for hand_name, positions in zero_positions.items():
                    if isinstance(positions, (list, tuple)) and len(positions) >= 16:
                        degrees = [math.degrees(p) if p is not None else None for p in positions]
                        print(f"{hand_name} hand positions after homing (deg): {degrees}")
            
        else:
            print(f"GaiaHand20 dual-hand connection failed (left: {ports_config['left']}, right: {ports_config['right']})")
            
    except Exception as e:
        print(f"GaiaHand20 dual-hand get_joint_positions test failed: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if hand and hand.is_connected():
            print("Homing...")
            hand.hand_zero()
            time.sleep(1)
            print("Disabling all joints...")
            disable_success = hand.enable_all_motors_broadcast(False)
            print(f"Disable result: {'succeeded' if disable_success else 'failed'}")
            hand.close()


def test_gaiahand20_reset_zero(ports_config):
    """
    Test GaiaHand20 homing (16-joint version)
    
    ⭐ Recommended: GaiaHand20 is the currently maintained version
    
    Baud rate: 921600 (with main board, high-performance)
    """
    print("\n=== Test GaiaHand20 hand homing (16-joint version) ===")
    
    if not ports_config or not ports_config['right']:
        print("No available right-hand serial port; skipping homing test")
        return
    
    hand = None
    try:
        # Create right-hand GaiaHand20 instance
        # ⭐ Baud rate: 921600 (with main board, high-performance)
        # Without main board, use baudrate=230400
        hand = create_hand("gaiahand20", "right", port=ports_config['right'], baudrate=921600)
        
        if hand.connect():
            print(f"GaiaHand20 connected, starting homing test (serial port: {ports_config['right']})")
            
            # Set motor smoothing (device_id=255 broadcasts to all motors, level=3)
            # Smoothing range 0-5; higher is smoother
            set_motor_smooth_level(hand, device_id=255, level=3, description="post-connect init")
            
            # Wait for settings to take effect
            time.sleep(0.5)
            
            # Enable all joints
            print("Enabling all joints...")
            enable_success = hand.enable_all_motors_broadcast(True)
            print(f"Enable result: {'succeeded' if enable_success else 'failed'}")
            
            if not enable_success:
                print("Enable failed; cannot continue test")
                return
            
            # Wait for enable to stabilize
            time.sleep(2)
            
            # Run homing
            print("Executing homing...")
            hand.hand_zero()
            print("Homing complete")
            
            time.sleep(2)
            
        else:
            print(f"GaiaHand20 connection failed (serial port: {ports_config['right']})")
            
    except Exception as e:
        print(f"GaiaHand20 homing test failed: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if hand and hand.is_connected():
            print("Homing...")
            hand.hand_zero()
            time.sleep(1)
            print("Disabling all joints...")
            disable_success = hand.enable_all_motors_broadcast(False)
            print(f"Disable result: {'succeeded' if disable_success else 'failed'}")
            hand.close()

def test_gaiahand15_move_joints_pos(ports_config):
    """
    Test GaiaHand15 move_joints_pos
    
    ⚠️ GaiaHand15 is no longer maintained; this function is for backward compatibility only
    Prefer test_gaiahand20_move_joints_pos()
    
    Baud rate:
    - Standard: 230400
    - Note: this function uses 921600, but standard is 230400
    """
    print("=== Test GaiaHand15 move_joints_pos ===")
    
    if not ports_config or not ports_config['right']:
        print("No available right-hand serial port; skipping single-hand test")
        return
    
    hand = None
    try:
        # Create right-hand GaiaHand15 instance
        # ⚠️ GaiaHand15 standard is 230400; 921600 here is example-only
        # Recommended: baudrate=230400
        hand = create_hand("gaiahand15", "right", port=ports_config['right'], baudrate=921600)

        if hand.connect():
            print(f"GaiaHand15 Connected (serial port: {ports_config['right']})")
            
            # Set motor smoothing (device_id=255 broadcasts to all motors, level=3)
            # Smoothing range 0-5; higher is smoother
            set_motor_smooth_level(hand, device_id=255, level=3, description="post-connect init")
            
            # Wait for settings to take effect
            time.sleep(0.5)
            
            # Enable all joints
            print("Enabling all joints...")
            enable_success = hand.enable_all_motors_broadcast(True)
            print(f"Enable result: {'succeeded' if enable_success else 'failed'}")
            
            if not enable_success:
                print("Enable failed; cannot continue test")
                return
            
            # Wait for enable to stabilize
            time.sleep(2)
            
            # Test single-hand mode — 15 joints (non-broadcast, default)
            print("\n--- Test single-hand mode (non-broadcast) ---")
            
            # Test single-hand mode — custom positions
            print("\n--- Test single-hand mode (custom positions) ---")
            
            # Custom positions: different angle per finger (radians)
            custom_positions = [
                # Thumb 3 joints
                0.0, math.radians(27.0), math.radians(43.0),
                # Index 3 joints
                0.0, math.radians(43.0), math.radians(56.0),
                # Middle 3 joints
                0.0, math.radians(33.0), math.radians(25.0),
                # Ring 3 joints
                0.0, math.radians(28.0), math.radians(18.0),
                # Little 3 joints
                0.0, math.radians(19.0), math.radians(26.0)
            ]
            
            print(f"Setting custom position data: {custom_positions}")
            success = hand.move_joints_pos(custom_positions, speed=1, use_broadcast=True)
            print(f"Custom position result: {'succeeded' if success else 'failed'}")
            
            # Wait 2 seconds
            time.sleep(2)
            
            # Test single-hand mode — gesture execution
            print("\n--- Test single-hand mode (gesture execution) ---")
            
            # Open-hand gesture (all joints extended)
            open_positions = [0.0] * 15
            print("Executing open-hand gesture...")
            success = hand.move_joints_pos(open_positions, speed=1, use_broadcast=True)
            print(f"Open-hand result: {'succeeded' if success else 'failed'}")
            
            time.sleep(2)
            
        else:
            print(f"GaiaHand15 connection failed (serial port: {ports_config['right']})")
            
    except Exception as e:
        print(f"GaiaHand15 test failed: {e}")
    finally:
        if hand and hand.is_connected():
            print("Homing...")
            hand.hand_zero()
            time.sleep(1)
            print("Disabling all joints...")
            disable_success = hand.enable_all_motors_broadcast(False)
            print(f"Disable result: {'succeeded' if disable_success else 'failed'}")
            hand.close()

def test_gaiahand15_double_move_joints_pos(ports_config):
    """
    Test GaiaHand15 dual-hand move_joints_pos
    
    ⚠️ GaiaHand15 is no longer maintained; this function is for backward compatibility only
    Prefer test_gaiahand20_double_move_joints_pos()
    
    Baud rate: 230400 (standard configuration)
    """
    print("\n=== Test GaiaHand15 dual-hand move_joints_pos ===")
    
    if not ports_config or not ports_config['left'] or not ports_config['right']:
        print("No available left/right serial ports; skipping dual-hand test")
        return
    
    hand = None
    try:
        # Create dual-hand GaiaHand15 instance
        # ⚠️ GaiaHand15 is no longer maintained; this function is for backward compatibility only
        # Baud rate: 230400 (standard configuration)
        hand = create_hand("gaiahand15", "double", left_port=ports_config['left'], right_port=ports_config['right'])
        
        if hand.connect():
            print(f"GaiaHand15 dual-hand connected (left: {ports_config['left']}, right: {ports_config['right']})")
            
            # Set motor smoothing (device_id=255 broadcasts to all motors, level=3)
            # Smoothing range 0-5; higher is smoother
            set_motor_smooth_level(hand, device_id=255, level=3, description="post-connect init")
            
            # Wait for settings to take effect
            time.sleep(0.5)
            
            # Enable all joints
            print("Enabling all joints...")
            enable_success = hand.enable_all_motors_broadcast(True)
            print(f"Enable result: {'succeeded' if enable_success else 'failed'}")
            
            if not enable_success:
                print("Enable failed; cannot continue test")
                return
            
            # Wait for enable to stabilize
            time.sleep(1)
            
            # Test dual-hand mode — 30 joints
            print("\n--- Test dual-hand mode (non-broadcast) ---")
            
            # Build dual-hand test positions
            # Order: first 15 = right hand, last 15 = left hand
            right_positions = [math.radians(5.0)] * 15  # Right hand all joints 5 deg (radians)
            left_positions = [math.radians(-5.0)] * 15   # Left hand all joints -5 deg (radians)
            double_positions = right_positions + left_positions
            
            print(f"Setting dual-hand position data: right{right_positions[:3]}..., left{left_positions[:3]}...")
            
            # Use non-broadcast mode
            success = hand.move_joints_pos(double_positions, speed=0.5, use_broadcast=False)
            print(f"Dual-hand non-broadcast result: {'succeeded' if success else 'failed'}")
            
            time.sleep(2)
            
            # Use broadcast mode
            print("\n--- Test dual-hand mode (broadcast) ---")
            success = hand.move_joints_pos(double_positions, speed=0.5, use_broadcast=True)
            print(f"Dual-hand broadcast result: {'succeeded' if success else 'failed'}")
            
            time.sleep(2)
            
            # Test dual-hand mode — custom positions
            print("\n--- Test dual-hand mode (custom positions) ---")
            
            # Right hand: thumb flex, other fingers extended (radians)
            right_custom = [
                # Thumb 3 joints
                0.0, math.radians(45.0), math.radians(45.0),
                # Other fingers 3 joints each
                0.0, 0.0, 0.0,  # Index
                0.0, 0.0, 0.0,  # Middle
                0.0, 0.0, 0.0,  # Ring
                0.0, 0.0, 0.0   # Little
            ]
            
            # Left hand: index flex, other fingers extended (radians)
            left_custom = [
                # Thumb 3 joints
                0.0, 0.0, 0.0,
                # Index 3 joints
                0.0, math.radians(45.0), math.radians(45.0),
                # Other fingers 3 joints each
                0.0, 0.0, 0.0,  # Middle
                0.0, 0.0, 0.0,  # Ring
                0.0, 0.0, 0.0   # Little
            ]
            
            custom_double_positions = right_custom + left_custom
            print(f"Setting custom dual-hand positions: right thumb flex, left index flex")
            success = hand.move_joints_pos(custom_double_positions, speed=0.5, use_broadcast=False)
            print(f"Custom dual-hand position result: {'succeeded' if success else 'failed'}")
            
            time.sleep(2)
            
            # Test dual-hand mode — gesture execution
            print("\n--- Test dual-hand mode (gesture execution) ---")
            
            # Dual-hand motion (radians)
            double_fist = [math.radians(10.0)] * 30
            print("Executing dual-hand fist gesture...")
            success = hand.move_joints_pos(double_fist, speed=0.5, use_broadcast=False)
            print(f"Dual-hand fist result: {'succeeded' if success else 'failed'}")
            
            time.sleep(2)
            
            # Dual-hand homing
            double_open = [0.0] * 30
            print("Executing dual-hand open gesture...")
            success = hand.move_joints_pos(double_open, speed=0.5, use_broadcast=True)
            print(f"Dual-hand open result: {'succeeded' if success else 'failed'}")
            
            time.sleep(2)
            
        else:
            print(f"GaiaHand15 dual-hand connection failed (left: {ports_config['left']}, right: {ports_config['right']})")
            
    except Exception as e:
        print(f"GaiaHand15 dual-hand test failed: {e}")
    finally:
        if hand and hand.is_connected():
            print("Homing...")
            hand.hand_zero()
            time.sleep(1)
            print("Disabling all joints...")
            disable_success = hand.enable_all_motors_broadcast(False)
            print(f"Disable result: {'succeeded' if disable_success else 'failed'}")
            hand.close()

def test_gaiahand15_smooth_transition(ports_config):
    """
    Test GaiaHand15 smooth transition
    
    ⚠️ GaiaHand15 is no longer maintained; this function is for backward compatibility only
    Prefer test_gaiahand20_smooth_transition()
    
    Baud rate:
    - Standard: 230400
    - Note: this function uses 921600, but standard is 230400
    """
    print("\n=== Test GaiaHand15 smooth transition ===")
    
    if not ports_config or not ports_config['right']:
        print("No available right-hand serial port; skipping smooth transition test")
        return
    
    hand = None
    try:
        # Create right-hand GaiaHand15 instance
        # ⚠️ GaiaHand15 standard is 230400; 921600 here is example-only
        # Recommended: baudrate=230400
        hand = create_hand("gaiahand15", "right", port=ports_config['right'], baudrate=921600)
        
        if hand.connect():
            print(f"GaiaHand15 connected, starting smooth transition test (serial port: {ports_config['right']})")
            
            # Set motor smoothing (device_id=255 broadcasts to all motors, level=3)
            # Smoothing range 0-5; higher is smoother
            set_motor_smooth_level(hand, device_id=255, level=3, description="post-connect init")
            
            # Wait for settings to take effect
            time.sleep(0.5)
            
            # Enable all joints
            print("Enabling all joints...")
            enable_success = hand.enable_all_motors_broadcast(True)
            print(f"Enable result: {'succeeded' if enable_success else 'failed'}")
            
            if not enable_success:
                print("Enable failed; cannot continue test")
                return
            
            # Wait for enable to stabilize
            time.sleep(1)
            
            # Define start and end positions (radians)
            start_positions = [0.0] * 15
            end_positions = [
                # Thumb 3 joints
                0.0, math.radians(27.0), math.radians(43.0),
                # Index 3 joints
                0.0, math.radians(43.0), math.radians(56.0),
                # Middle 3 joints
                0.0, math.radians(33.0), math.radians(25.0),
                # Ring 3 joints
                0.0, math.radians(28.0), math.radians(18.0),
                # Little 3 joints
                0.0, math.radians(19.0), math.radians(26.0)
            ]
            
            print("Running smooth transition: extended to flexed")
            
            # Transition in 5 steps (non-broadcast, more stable)
            for i in range(6):
                t = i / 5.0
                positions = []
                for j in range(15):
                    pos = start_positions[j] + (end_positions[j] - start_positions[j]) * t
                    positions.append(pos)
                
                print(f"Step {i+1}/6: transition progress {t*100:.1f}%")
                hand.move_joints_pos(positions, speed=0.5, use_broadcast=True)
                time.sleep(0.05)
                current_positions = hand.get_joint_positions()
                print(f"Current joint positions=====================: {current_positions}")

            print("Smooth transition complete")
            
            time.sleep(2)
            
            # Reverse transition: flexed to extended
            print("Running reverse transition: flexed to extended")
            
            for i in range(10):
                t = i / 10.0
                positions = []
                for j in range(15):
                    pos = end_positions[j] + (start_positions[j] - end_positions[j]) * t
                    positions.append(pos)
                
                print(f"Step {i+1}/6: transition progress {t*100:.1f}%")
                hand.move_joints_pos(positions, speed=0.5, use_broadcast=True)
                time.sleep(0.05)
                current_positions = hand.get_joint_positions()
                print(f"Current joint positions======================: {current_positions}")
            
            print("Reverse transition complete")

            time.sleep(2)
            
        else:
            print(f"GaiaHand15 connection failed (serial port: {ports_config['right']})")
            
    except Exception as e:
        print(f"GaiaHand15 smooth transition test failed: {e}")
    finally:
        if hand and hand.is_connected():
            print("Homing...")
            hand.hand_zero()
            time.sleep(1)
            print("Disabling all joints...")
            disable_success = hand.enable_all_motors_broadcast(False)
            print(f"Disable result: {'succeeded' if disable_success else 'failed'}")
            hand.close()

def test_reset_pose_zero(ports_config):
    """
    Test hand homing (GaiaHand15)
    
    ⚠️ GaiaHand15 is no longer maintained; this function is for backward compatibility only
    Prefer test_gaiahand20_reset_zero()
    
    Baud rate: 230400 (standard configuration)
    """
    print("\n=== Test hand homing ===")
    
    if not ports_config or not ports_config['right']:
        print("No available right-hand serial port; skipping homing test")
        return
    
    hand = None
    try:
        # Create right-hand GaiaHand15 instance
        hand = create_hand("gaiahand15", "right", port=ports_config['right'])
        
        if hand.connect():
            print(f"GaiaHand15 connected, starting homing test (serial port: {ports_config['right']})")
            
            # Set motor smoothing (device_id=255 broadcasts to all motors, level=3)
            # Smoothing range 0-5; higher is smoother
            set_motor_smooth_level(hand, device_id=255, level=3, description="post-connect init")
            
            # Wait for settings to take effect
            time.sleep(0.5)
            
            # Enable all joints
            print("Enabling all joints...")
            enable_success = hand.enable_all_motors_broadcast(True)
            print(f"Enable result: {'succeeded' if enable_success else 'failed'}")
            
            if not enable_success:
                print("Enable failed; cannot continue test")
                return
            
            # Wait for enable to stabilize
            time.sleep(2)
            
            # Run homing
            print("Executing homing...")
            hand.hand_zero()
            print("Homing complete")
            
            time.sleep(2)
            
        else:
            print(f"GaiaHand15 connection failed (serial port: {ports_config['right']})")
            
    except Exception as e:
        print(f"GaiaHand15 homing test failed: {e}")
    finally:
        if hand and hand.is_connected():
            print("Homing...")
            hand.hand_zero()
            time.sleep(1)
            print("Disabling all joints...")
            disable_success = hand.enable_all_motors_broadcast(False)
            print(f"Disable result: {'succeeded' if disable_success else 'failed'}")
            hand.close()


def main():
    """
    Main test entry
    
    ⭐ Recommended: GaiaHand20 (16-joint version), currently the main maintained release
    ⚠️ GaiaHand15 (15-joint) is no longer maintained; related tests kept for compatibility
    
    Baud rate configuration:
    - GaiaHand15: 230400 (standard configuration)
    - GaiaHand20 without main board: 230400 (default configuration)
    - GaiaHand20 with main board: 921600 (high-performance configuration)
    
    Usage:
    1. Pick test functions matching your hardware
    2. Uncomment the desired test functions to run tests
    3. GaiaHand20 tests are preferred by default
    """
    print("Starting GaiaHand tests")
    print("=" * 50)
    print("Recommended: GaiaHand20 (16-joint version), currently maintained")
    print("GaiaHand15 (15-joint version) is no longer maintained")
    print("=" * 50)

    # Set log level (optional: uncomment test_log_management() to exercise log management)
    # test_log_management()
    set_log_level('INFO') # DEBUG INFO WARNING ERROR CRITICAL
    # enable_all_logs()
    # disable_all_logs()
    # set_both_output()

    # Detect serial ports
    ports_config = detect_serial_ports()
    
    if not ports_config:
        print("Serial port detection failed; cannot run tests")
        return
    
    print(f"\nUsing serial port config:")
    print(f"  Left: {ports_config['left']}")
    print(f"  Right: {ports_config['right']}")
    print(f"  Available ports: {ports_config['available']}")
    
    print("\nBaudrate notes:")
    print("  - GaiaHand15: 230400 (standard)")
    print("  - GaiaHand20 without main board: 230400 (default)")
    print("  - GaiaHand20 with main board: 921600 (high-performance)")

    # ==================== GaiaHand20 (16-joint) tests ⭐ recommended ====================
    print("\n" + "=" * 50)
    print("GaiaHand20 (16-joint) tests - recommended")
    print("=" * 50)

    # Test GaiaHand20 instance creation
    # test_gaiahand20_create_hand(ports_config)
    
    # Test GaiaHand20 status (connection, joint positions, motor status)
    # test_gaiahand20_get_status(ports_config)

    # Test GaiaHand20 joint limits (no hardware connection or motion by default)
    # test_gaiahand20_joint_limits(ports_config)
    # To verify limit clamping on hardware, use:
    # test_gaiahand20_joint_limits(ports_config, connect_for_motion=True)
    
    # Test GaiaHand20 single-hand get_joint_positions (enabled by default)
    # test_gaiahand20_get_joint_positions(ports_config)

    # Test GaiaHand20 get_joints_pos_vel (protocol keys 3=position 5=velocity; same connection options as above)
    test_gaiahand20_get_joints_pos_vel(ports_config)
    
    # Test GaiaHand20 single-hand list format — baud 230400 (no main board)
    # test_gaiahand20_move_joints_pos_list(ports_config)
    
    # Test GaiaHand20 single-hand dict format — baud 230400 (no main board)
    # test_gaiahand20_move_joints_pos_dict(ports_config)
    
    # Test GaiaHand20 dual-hand list format — baud 230400 (no main board)
    # test_gaiahand20_double_move_joints_pos(ports_config)
    
    # Test GaiaHand20 dual-hand dict format — baud 230400 (no main board)
    # test_gaiahand20_double_move_joints_pos_dict(ports_config)
    
    # Test GaiaHand20 dual-hand get positions — baud 230400 (no main board)
    # test_gaiahand20_double_get_joint_positions(ports_config)
    
    # Test GaiaHand20 smooth transition — baud 921600 (with main board)
    # test_gaiahand20_smooth_transition(ports_config)
    
    # Test GaiaHand20 homing — baud 921600 (with main board)
    # test_gaiahand20_reset_zero(ports_config)
    
    # ==================== GaiaHand15 (15-joint) tests ⚠️ deprecated ====================
    # print("\n" + "=" * 50)
    # print("GaiaHand15 (15-joint) tests - deprecated, compatibility only")
    # print("=" * 50)
    
    # Test homing — baud 230400 (standard configuration)
    # test_reset_pose_zero(ports_config)
    
    # Test GaiaHand15 single-hand — baud 921600 in example (standard is 230400)
    # test_gaiahand15_move_joints_pos(ports_config)
    
    # Test GaiaHand15 dual-hand — baud 230400 (standard)
    # test_gaiahand15_double_move_joints_pos(ports_config)
    
    # Test GaiaHand15 smooth transition — baud 921600 in example (standard is 230400)
    # test_gaiahand15_smooth_transition(ports_config)
    
    # print("\n" + "=" * 50)
    # print("All tests complete")
    # print("Recommended: use GaiaHand20 (16-joint version) for development")

if __name__ == "__main__":
    main()
