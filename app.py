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
model = "gpt-4-1106-preview"
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
    '''
    Function to generate two fake responses based on the provided question and real_response.
    Uses LLM Chaining to break task into two steps: content generation and syntax matching.
    '''

    num_tokens = int(0.75 * len(real_response.split(" ")))

    system_message1 = (
        '''
        Generate two fake responses to a question to match the style of the real response closely.

        Follow these instructions:
        1. Use similar tone of voice and wording as the real response.
        2. Follow the same structure and manner of speaking as the real response.
        3. Come up with a new answer and be creative! The core idea of the fake responses should be different from the real response.
        4. Avoid complicated words, and be straightforward.

        Separate the two responses by a newline.
        '''
    )

    user_message = f'''Question = {question}\n\nReal response = {real_response}\n\nFake responses='''
    test_messages = [{"role": "system", "content": system_message1},
                     {"role": "user", "content": user_message}]

    fake_responses = openai.ChatCompletion.create(
        model=model,
        messages=test_messages,
        temperature=0.4
    )['choices'][0]['message']['content']

    system_message2 = (
        '''
        Modify two fake responses to a question to match the syntax of the real response closely.

        Follow these instructions:
        1. Keep the same brevity as the real response. If your response is less than {num_tokens - 5} tokens, add more detail. If your response is above {num_tokens + 5} tokens, take out some detail.
        2. Follow the same syntax as the real response. Use similar forms of punctuation and word choice. Follow the same language patterns: if the user does not capitalize or use punctuation, do the same.
        3. Retain the same meaning as the current fake responses. Only change the responses to be more realistic from a romantic partner.
        '''
    )

    user_message2 = f"""Question = {question}\n\nReal response = {real_response}\n\nFake responses= {fake_responses}\n\nModified fake responses="""
    test_messages2 = [{"role": "system", "content": system_message2},
                     {"role": "user", "content": user_message2}]

    fake_responses_modified = openai.ChatCompletion.create(
        model=model,
        messages=test_messages2,
        temperature=0.3
    )['choices'][0]['message']['content']

    answers = fake_responses_modified.split('\n\n') + [real_response]
    random.shuffle(answers)

    if answers[0] == real_response:
        return_tuple = ('A',) + tuple(answers)
    elif answers[1] == real_response:
        return_tuple = ('B',) + tuple(answers)
    else: return_tuple = ('C',) + tuple(answers)

    return return_tuple
