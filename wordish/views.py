from django.shortcuts import render
from wordish.static.util import five_letter_words

def __process_param_post(request, word):
  # print(f'In process param post with word {word}')
  if word not in request:
    raise Exception(f'param \'{word}\' was not sent in POST request')

  if not request[word]:
    raise Exception('Blank word!')
  
  word_param = request[word]
  if word_param not in five_letter_words.Five_Letter_Words.words:
    raise Exception('are we on the right page?')
  return word_param

def __process_param(request, word):
  # print(f'In process param with word {word}')
  if word not in request:
    raise Exception(f'param \'{word}\' was not sent in POST request')

  if not request[word]:
    raise Exception('Blank word!')
  
  word_param = request[word]
  if word_param not in five_letter_words.Five_Letter_Words.words:
    raise Exception('Invalid input!')
  return word_param

def compute_background(guess_word, target_word):
  # print(f"in compute background with guess={guess_word} and target={target_word}")
  if guess_word[0] == '':
    colors = ["white" for i in range(5)]
    return colors

  guess = list(guess_word.upper())
  target = list(target_word.upper())
  colors = ['' for i in range(5)]
  # greens
  for i in range(5):
    if (guess[i] == target[i]):
      colors[i] = "green"
      guess[i] = ''
      target[i] = ''

  # yellow
  for i in range(5):
    if (guess[i] != '' or target[i] != ''):
      if guess[i] in target:
        colors[i] = "yellow"
        # remove occurance from the target string so
        # subsequent check is invalid
        target[target.index(guess[i])] = ''
        guess[i] = ''

  # grey
  for i in range(5):
    if guess[i] != '':
      colors[i] = "grey"
  return colors

def init_matrix(start, stop):
  matrix = []
  for row in range(start, stop):
    matrix_row = []
    colors = ['white' for i in range(5)]
    for column in range(5):
      cell = {"id": f'cell_{row}_{column}', "letter": '', "color": colors[column]}
      matrix_row.append(cell)
    matrix.append(matrix_row)
  return matrix

def compute_score(colors):
  score = 0
  for color in colors:
    if color == 'green':
      score += 1
  return score

def __compute_context(target, guesses):
  # print(f'in compute_context with target {target} and guesses={guesses}')
  win = False
  finish = False
  attempts = len(guesses)
  if attempts == 0:
    status = "start"
    matrix = init_matrix(0, 6)

  else:
    print("Valid input!")
    status = "Valid Input!"
    matrix = []
    for row in range(len(guesses)):
      matrix_row = []
      colors = compute_background(guesses[row], target)
      for column in range(5):
        cell = {"id": f'cell_{row}_{column}', "letter": guesses[row][column], "color": colors[column]}
        matrix_row.append(cell)
      matrix.append(matrix_row)

      score = compute_score(colors)
      if score == 5:
        status = 'You Win!'
        win = True
        finish = True

    if not finish:
      matrix[attempts:] = init_matrix(attempts, 6)
  
  if (attempts == 6 and (not win)):
    status = 'You lose!'
    finish = True

  context = {
    "status": status,
    "matrix": matrix,
    "target": target,
    "old_guesses": guesses,
    "attempts": attempts+1,
    "finish": finish
  }
  return context


# Create your views here.

# displays the start screen on the first GET hit to the app
# subsequently calls the 'game' view when a valid target is
# submitted
def start_action(request):
  context = {}
  if request.method == 'GET':
    context['message'] = 'welcome to Wordish!'
    return render(request, "wordish/start.html", context)
  
  try:
    target = __process_param(request.POST, 'target')
    context = __compute_context(target, guesses=list())
    return render(request, "wordish/game.html", context)
  
  except  Exception as e:
    context = {"message": 'error : ' + str(e)}
    return render(request, "wordish/start.html", context)


def __process_old_guesses(request):
  old_guesses = request.get('old_guesses').split(',')
  if old_guesses == ['']:
    old_guesses = []
  
  for guess in old_guesses:
    if guess not in five_letter_words.Five_Letter_Words.words:
      raise Exception('are we on the right page?')
    
  return old_guesses

def add_guess(old_guesses, new_guess):
  old_guesses.append(new_guess)
  return old_guesses


def guess_action(request):
  """
  takes a user-inputted guess word and processes it to
  update score and the display grid
  """
  if request.method == "GET":
    context = {"message": "You're hacking. Try again!"}
    return render(request, "wordish/start.html", context)
  
  try:
    target = __process_param_post(request.POST, "target")
    old_guesses = __process_old_guesses(request.POST)
  except Exception as e:
    return render(request, "wordish/start.html", {"message": f" error: {e}"})
  
  try:

    new_guess = __process_param(request.POST, "new-guess")
    old_guesses = add_guess(old_guesses, new_guess)
    context = __compute_context(target, old_guesses)
    if (context['finish']):
      context['attempts'] = len(old_guesses) if len(old_guesses) <= 6 else 7
      return render(request, 'wordish/end.html', context)

  except Exception as e:
    context = __compute_context(target, old_guesses)
    context['status'] = 'error : ' + str(e)
  
  return render(request, 'wordish/game.html', context)
