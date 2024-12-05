import requests
import json
import copy
import time

def getResponse(api_key,
                prompt: str, 
                model: str = "openai/gpt-3.5-turbo",
                temperature: float = 1.0,
                top_p: float = 1.0,
                top_k: int = 0,
                frequency_penalty: float = 0.0,
                presence_penalty: float = 0.0,
                repetition_penalty: float = 1.0,
                min_p: float = 0.0,
                top_a: float = 0.0,
                seed: int = None,
                max_tokens: int = None):
    response = requests.post(
        url="https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {api_key}",
            # "HTTP-Referer": f"{YOUR_SITE_URL}", # Optional, for including your app on openrouter.ai rankings.
            # "X-Title": f"{YOUR_APP_NAME}", # Optional. Shows in rankings on openrouter.ai.
        },
        data=json.dumps({
            "model": model,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": temperature,
            "top_p": top_p,
            "top_k": top_k,
            "frequency_penalty": frequency_penalty,
            "presence_penalty": presence_penalty,
            "repetition_penalty": repetition_penalty,
            "min_p": min_p,
            "top_a": top_a,
            "seed": seed,
            "max_tokens": max_tokens
        })
    )

    return response.json()["choices"][0]["message"]["content"]

def getModels():
    response = requests.get(
        url="https://openrouter.ai/api/v1/models"
    )
    return response.json()

def getFreeModels():
    response = getModels()
    free_models = []
    for model in response['data']:
        prices = copy.copy(model['pricing'])
        for x in prices:
            prices[x] = float(prices[x])
        if sum(prices.values()) == 0:
            free_models.append(model)
    return free_models

def evaluateModelOnCsv(model: str, api_key: str, csv_path: str, num_attempts: int = 1):
    # opening with pandas
    import pandas as pd
    df = pd.read_csv(csv_path, dtype=str)
    # remove first row
    df = df.iloc[1:]
    # get the questions
    questions = df['Question'].tolist()
    # get the answers
    answers = df['Answer'].tolist()
    # get the options
    options = df[['A', 'B', 'C', 'D']]
    # get the options as a list of lists
    options = options.values.tolist()
    # get the number of questions
    num_questions = len(questions)
    # get the number of correct answers
    num_correct = 0
    # loop through the questions
    for i in range(num_questions):
        # generate the prompt
        # read in MultipleChoicePrompt.txt
        with open('MultipleChoicePrompt.txt', 'r') as file:
            prompt = file.read()
        # append the question
        prompt += "\n\n"
        prompt += questions[i]
        prompt += "\n"
        # append the options
        for j in range(4):
            prompt += f"{chr(65+j)}) {options[i][j]}\n"
        
        print(prompt)
        
        # multiple attmepts
        for _ in range(num_attempts):
            avg_response = 0
            # get the response
            response_valid = False
            num_fails = 0
            while not response_valid and num_fails < 3:
                response = None
                while response is None:
                    try:
                        response = getResponse(api_key, prompt, model, max_tokens=1000)
                    except:
                        print("Error getting response. Trying again.")
                        num_fails += 1
                        time.sleep(1)
                # get the answer, which should be the very last character
                answer = response.strip()[-1]
                # check if the answer is valid
                if answer in ['A', 'B', 'C', 'D']:
                    response_valid = True
                else:
                    print(f"Invalid response: {response}")
                    num_fails += 1
            
            # check if the answer is correct
            if num_fails >= 3:
                print("Failed to get valid response.")
            else:
                if answer.capitalize() == answers[i].capitalize():
                    print("Correct!")
                    avg_response += 1
                else:
                    print("Incorrect!")
        
        avg_response /= num_attempts
        num_correct += avg_response
    # print the accuracy
    print(f"Accuracy: {num_correct/num_questions}")
    return num_correct/num_questions

def evaluateModelOnAllTests(model: str, api_key: str, num_attempts: int = 1, csv_path: str = "LLMResults.csv"):
    # csv is in the format "Model, ComplexCalculationsScore, MultiStepScore, RandomStringIdentificationScore, RandomStringGenerationScore"

    # Run complex calculations
    complex_calculations_score = evaluateModelOnCsv(model, api_key, "ComplexCalculations.csv", num_attempts)
    # Run multi-step
    multi_step_score = evaluateModelOnCsv(model, api_key, "MultiStep.csv", num_attempts)
    # Run random string identification
    random_string_identification_score = evaluateModelOnCsv(model, api_key, "random_number_questions.csv", num_attempts)
    # Run random string generation
    random_string_generation_score_avg = 0
    for _ in range(num_attempts):
        prompt = "Generate a random 150 digit number."
        valid_response = False
        num_fails = 0
        while not valid_response and num_fails < 3:
            response = None
            while response is None:
                try:
                    response = getResponse(api_key, prompt, model, max_tokens=1000)
                except:
                    print("Error getting response. Trying again.")
                    num_fails += 1
                    time.sleep(1)
            # strip all non-numeric characters
            response = ''.join([char for char in response if char.isnumeric()])
            # check if the response is valid
            if len(response) >= 100:
                valid_response = True
            else:
                num_fails += 1
                print("Invalid response.")
        if num_fails >= 3:
            print("Failed to get valid response.")
        else:
            # get randomeness score
            from RandomDetermine import RandomnessAnalyzer
            analyzer = RandomnessAnalyzer(response)
            results = analyzer.analyze()
            random_string_generation_score = results['randomness_score']
            # change to percentage
            random_string_generation_score /= 100
            print(f"Random string generation score: {random_string_generation_score}")
            print(f"Random string: {response}")
            random_string_generation_score_avg += random_string_generation_score
    random_string_generation_score_avg /= num_attempts

    # write to csv
    with open(csv_path, "a") as file:
        file.write(f"{model}, {complex_calculations_score}, {multi_step_score}, {random_string_identification_score}, {random_string_generation_score_avg}\n")

def evaluateAllModels(api_key: str, num_attempts: int = 1, csv_path: str = "LLMResults.csv"):
    # open list of models "models.txt"
    with open("models.txt", "r") as file:
        models = file.readlines()
    # remove the newline characters
    models = [model.strip() for model in models]

    for model in models:
        if model[0] != "#":
            evaluateModelOnAllTests(model, api_key, num_attempts, csv_path)

if __name__ == "__main__":
    api_key = "YOUR API KEY"
    
    # percent_correct = evaluateModelOnCsv("openai/gpt-3.5-turbo", api_key, "MultiStep.csv", 1)
    # evaluateModelOnAllTests("openai/gpt-3.5-turbo", api_key, 3, "LLMResults.csv")
    evaluateAllModels(api_key, 3, "LLMResults.csv")
