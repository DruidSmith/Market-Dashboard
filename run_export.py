"""
Generate AI-ready market analysis export.
"""

from src.export_generator import ExportGenerator


def main():
    """Main execution function."""
    print("="*70)
    print("📊 MARKET ANALYSIS EXPORT GENERATOR")
    print("="*70)
    
    try:
        generator = ExportGenerator()
        output_path = generator.export_to_file()
        
        print(f"\n✅ Export complete!")
        print(f"📄 File: {output_path}")
        print(f"📏 Size: {output_path.stat().st_size:,} bytes")
        
        print("\n" + "="*70)
        print("💡 NEXT STEPS:")
        print("="*70)
        print("1. Open the file in a text editor")
        print("2. Copy the entire contents")
        print("3. Paste into your preferred AI assistant (ChatGPT, Claude, etc.)")
        print("4. The AI will analyze and provide:")
        print("   - Buy/Sell/Hold recommendations")
        print("   - Specific stop loss levels")
        print("   - Risk assessment")
        print("   - AI bubble warnings")
        print("   - Recession probability")
        print("="*70)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        print("="*70)


if __name__ == "__main__":
    main()