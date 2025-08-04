#!/usr/bin/env python3
"""
Test the dB to normalized transformation
"""

def transform_db_to_normalized(db_value):
    """Transform dB value to normalized 0.0-1.0 range for X32"""
    try:
        # Convert dB to linear scale, then normalize
        # dB range is typically -60 to +10, normalize to 0.0-1.0
        if db_value <= -60:
            return 0.0
        elif db_value >= 10:
            return 1.0
        else:
            # Convert dB to linear: 10^(dB/20)
            linear = 10 ** (db_value / 20.0)
            # Normalize to 0.0-1.0 range
            # -60dB = 0.001 linear = 0.0 normalized
            # 0dB = 1.0 linear = 0.5 normalized  
            # +10dB = 3.16 linear = 1.0 normalized
            normalized = (linear - 0.001) / (3.16 - 0.001)
            return max(0.0, min(1.0, normalized))
    except:
        # Fallback to simple mapping
        if db_value <= -60:
            return 0.0
        elif db_value >= 10:
            return 1.0
        else:
            # Simple linear mapping
            return (db_value + 60) / 70.0

def main():
    print("🧪 Testing dB to normalized transformation...")
    print()
    
    # Test various dB values
    test_values = [
        -60.0, -40.0, -20.0, -10.0, -5.0, 0.0, 5.0, 10.0
    ]
    
    for db in test_values:
        normalized = transform_db_to_normalized(db)
        print(f"📊 {db:+6.1f} dB → {normalized:.3f} normalized")
    
    print()
    print("🎯 Transformation test completed!")

if __name__ == "__main__":
    main() 