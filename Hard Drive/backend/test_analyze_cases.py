from services.mistral_service import analyze_cases

def test_analyze_cases():
    # Example test case
    test_case = "A case involving medical malpractice, where a doctor was negligent during surgery."

    # Get predictions
    predictions = analyze_cases(test_case)

    # Print the predictions
    print("Predictions:", predictions)

# Run the test
if __name__ == "__main__":
    test_analyze_cases()

