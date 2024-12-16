import subprocess
import os
import sys
import time

def run_command(command, description):
    """Run a command and display its output in real-time"""
    print(f"\n🚀 {description}...")
    process = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        shell=True
    )
    
    # Print output in real-time
    while True:
        output = process.stdout.readline()
        if output == '' and process.poll() is not None:
            break
        if output:
            print(output.strip())
    
    return process.poll()

def main():
    print("🍎 Apple Health Data Explorer")
    print("============================")
    
    # Check if processed_data directory exists
    if not os.path.exists("processed_data"):
        os.makedirs("processed_data")
    
    try:
        # Run preprocessing
        preprocess_result = run_command(
            "python preprocess_health_data.py",
            "Preprocessing health data"
        )
        
        if preprocess_result != 0:
            print("❌ Error during preprocessing. Please check the error messages above.")
            sys.exit(1)
        
        print("✅ Preprocessing completed successfully!")
        
        # Small delay to ensure all files are written
        time.sleep(1)
        
        # Run Streamlit app
        print("\n🌟 Starting the Streamlit app...")
        app_result = run_command(
            "streamlit run app.py",
            "Launching Apple Health Data Explorer"
        )
        
        if app_result != 0:
            print("❌ Error launching the app. Please check the error messages above.")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n\n👋 Shutting down...")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ An error occurred: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()