from flask import Flask, jsonify, request
import random
# import tiktoken
import openai
import os
import re

app = Flask(__name__)

questions = [
    # Adapted from: https://www.nytimes.com/2015/01/09/style/no-37-big-wedding-or-small.html
    "Given the choice of anyone in the world, whom would you want as a dinner guest?",
    "Would you like to be famous? In what way?",
    "Before making a telephone call, do you ever rehearse what you are going to say? Why?",
    "What would constitute a 'perfect' day for you?",
    "When did you last sing to yourself?",
    "Do you have a secret hunch about how you will die?",
    "For what in your life do you feel most grateful?",
    "If you could change anything about the way you were raised, what would it be?",
    "If you could wake up tomorrow having gained any one quality or ability, what would it be?",
    "If a crystal ball could tell you the truth about anything, what would you want to know?",
    "Is there something that you've dreamed of doing for a long time?",
    "What is the greatest accomplishment of your life?",
    "What do you value most in a friendship?",
    "What is your most treasured memory?",
    "What is your most terrible memory?",
    "How close are you to your family?",
    "Complete this sentence: 'I wish I had someone with whom I could share...'",
    "What's an embarrassing moment in your life?",
    "When did you last cry?",
    "If you were to die today, what would you most regret not having told someone?",
    "Your house catches fire. After saving your loved ones and pets, what one item are you saving and why?",

    # Adapted from: https://www.brides.com/questions-to-ask-your-partner-5105339
    "What's the biggest risk you've ever taken that didn't pay off?",
    "What's something you would love to try but are too afraid?",
    "Would you rather spend a day with your kindergarten self or your elderly self? Why?",
    "Do you have any recurring dreams? What are they?",
    "Who was your childhood hero? Why did you admire them?",
    "What's something that's missing from your life?",
    "What would you title your memoir?",
    "If you could travel back in time to any place and time, when and where would you go?",
    "When you were little, what did you want to be when you grew up?",
    "What's the best piece of advice you've ever received?",
    "If you could solve one problem, what would it be?",
    "If you could know one thing about your future, what would it be?",
    "How have you changed in the past year?",
    "Are there any habits you wish you could break?",
    "What's one thing you've tried that you wouldn't try again?",
    "What's your most guilty pleasure?",
    "What mundane tasks or chores do you secretly enjoy doing?",
    "What are your simple pleasures in life?",
    "What's the best compliment you've ever received?",

    # Self-compiled
    "What was one thing that made you smile today?",
    "Where do you see us in 5 years?",
    "What can I do to be a better partner?",
    "How has being long distance negatively or positively affected your daily life?",
    "Are you unsatisfied with anything in our relationship? If so, what?",
    "Who is your biggest role model today?",
    "What keeps you motivated?",
    "How do you handle stress when you are alone?",
    "If you could be any fruit, what would it be and why?",
    "What's one thing you are proud of yourself for?"
]

@app.route('/')
def home():
    return 'Welcome to bae-i!'

@app.route('/question')
def retrieve_question():
    return questions[random.randint(0, len(questions)-1)]

# Load OpenAI API key and model
openai.api_key = os.getenv("OPENAI_API_KEY")
model = "gpt-3.5-turbo"
# encoding = tiktoken.encoding_for_model(model)

@app.route('/gpt', methods=['POST'])
def retrieve_responses_endpoint():
    question = request.json['question']
    real_response = request.json['real_response']
    print(question, real_response)
    if not (question and real_response):
        return jsonify({"error": "Both 'question' and 'real_response' fields are required."}), 400

    answer, response1, response2, response3 = retrieve_responses(question, real_response)
    return jsonify({
        "answer": answer,
        "first": response1,
        "second": response2,
        "third": response3,
    })

def retrieve_responses(question, real_response):
    num_tokens = int(0.75 * len(real_response.split(" ")))

    """
    Function to generate two fake responses based on the provided question and real_response.
    """
    system_message = (f"""
      You are assisting a long-distance couple, Player A and Player B.
      Player A will pose a question, to which Player B will respond.
      Your task is to craft a response that mirrors the style of Player B closely.
      For this exercise, Player A will have to discern which of the responses, yours or Player B's, is authentic.
      Use similar tone of voice and wording. Keep the same brevity as the real response. Follow the same syntax and manner of speaking, but come up with a new answer and be creative!
      Avoid complicated words, and be straightforward.
      Your generated message should be plausible yet subtly confusing, matching Player B's level of detail and brevity.
      It is imperative that your response constitutes a complete and well-articulated sentence.
      Absolutely do not end on a hanging sentence fragment.
      Make sure your response is between {num_tokens} and {num_tokens + 5} tokens.
                      
      Use these examples to guide your response:
    
      Example 1: Question = "What was the best thing that happened to you this week?"
      Real response = "Adopting a puppy!"
      Fake response 1 = "Going to yoga class! [eos]"
      Fake response 2 = "Finding my new favorite song! [eos]"

      Example 2: Question = "What are you unsatisfied with in our relationship?"
      Real response = "not anything big but i wish we could do more fun things together like when we first started dating..."
      Fake response 1 = "nothing, i'm very happy with where we're at [eos]"
      Fake response 2 = "we're always having fun but sometimes i wish we could talk more openly about deeper topics [eos]"
      
      Example 3: Question = "Where do you see us in 10 years?"
      Real response = "i don't like to think about the future like that."
      Fake response 1 = "we'll probably be together still, hopefully with a family [eos]"
      Fake response 2 = "together or not, i hope we're both happy with thriving careers [eos]"
      """)
    user_message = f"""Question from Player A: {question}\n\nReal response by Player B: {real_response}\n\nFake response 1: """

    test_messages = [{"role": "system", "content": system_message},
                     {"role": "user", "content": user_message}]

    # num_tokens = len(encoding.encode(real_response))
    # num_tokens = 50
    response1 = openai.ChatCompletion.create(
        model=model,
        messages=test_messages,
        temperature=0.3,
        # max_tokens=num_tokens + 5
    )['choices'][0]['message']['content']

    user_message = f"""Question from Player A: {question}\n\nReal response by Player B: {real_response}\n\nFake response 1: {response1}\n\nFake response 2: """
    test_messages.pop()
    test_messages.append({"role": "user", "content": user_message})
    response2 = openai.ChatCompletion.create(
        model=model,
        messages=test_messages,
        temperature=0.4,
        # max_tokens=num_tokens + 5
    )['choices'][0]['message']['content']

    answers = [response1.split(' [eos]')[0], response2.split(' [eos]')[0], real_response]
    random.shuffle(answers)

    # Check the position of 'hello' in the shuffled list
    if answers[0] == real_response:
        return_tuple = ('A',) + tuple(answers)
    elif answers[1] == real_response:
        return_tuple = ('B',) + tuple(answers)
    else: return_tuple = ('C',) + tuple(answers)

    return return_tuple
