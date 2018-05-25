from functools import reduce 
import numpy as np
import pandas as pd
'''
texts = [['i', 'have', 'a', 'cat', 'apple'], 
        ['he', 'have', 'a', 'dog'], 
        ['he', 'and', 'i', 'have', 'a', 'cat', 'and', 'a', 'dog']]

dictionary = list(enumerate(set(list(reduce(lambda x, y: x + y, texts)))))
word_list = sorted([i[1] for i in dictionary],key=len)

dictionary_1 = [(0, 'a'), (1, 'i'), (2, 'he'), (3, 'and'), (4, 'cat'), (5, 'have'), (6, 'dog')]
word_list_1 = ['a', 'i', 'he', 'dog', 'and', 'cat', 'have']

def vectorize(text,dictionary,word_list):
	vector = np.zeros(len(dictionary))
	for w in text:
		if w in word_list:
			pass
		else:
			return ("New word found: %s" %w)
	for i,word in dictionary:
		num = 0
		for w in text:
			if w == word:
				num += 1

		if num:
			vector[i] = num
	return vector

df_list = []


for t in texts:
	if type(vectorize(t,dictionary_1,word_list_1)) is np.ndarray:
		df_list.append(pd.Series(vectorize(t,dictionary_1,word_list)))
	elif type(vectorize(t,dictionary_1,word_list_1)) is str:
		print (vectorize(t,dictionary_1,word_list_1))
	else:
		print('hmm')


print('aaabbb'.split('-'))
'''


##############

with open("./Data Files/EN_US.txt") as word_file:
    english_words = set(word.strip().lower() for word in word_file)
def is_word(word):
    return word.lower() in english_words

def get_english_words_out_of_string(string):
    output_list = []
    for splits in string.split(' '):
        if is_word(splits):
            output_list.append(splits.lower())
        else:
            break
    return output_list




text_1 = 'Dividend LU0913601281 AGIF INC GROW AMH2D'
text_2 = 'INTEREST-FIXED TERM LOAN Contract No: 3001-AA18091RSG5N|Interest rate: 0.810000%|Capital: 1,000,000,000.00|Period: 16.04.2018 - 01.05.2018|Days: 15/360'
text_3 = 'FOREX SPOT EUR/JPY 129.6910'
sr = pd.Series([text_1,text_2,text_3])
df = pd.DataFrame(sr)
df.columns =['test']
forex = (df['test'].str.extract("^([A-Z\s]*)\s",expand=True)) # for SPOT FX
interest = (df['test'].str.extract("^([A-Z]+-[A-Z]+[A-Z\s]*)\s",expand=True)) #For 'INTEREST-FIX TERM LOAN'
forex.columns = ['test']
interest.columns = ['test']
#combined = forex['test'].add(interest['test'],fill_value = 0)
forex_drop = forex.dropna()
forex_drop.loc[:,'test'] = forex_drop['test'].str.lower().str.split(' ')
interest_drop = interest.dropna()
interest_drop.loc[:,'test'] = interest_drop['test'].str.lower().str.split('-| ')
combined = pd.concat([forex_drop,interest_drop]).sort_index().reset_index()

max_length = combined['index'][len(combined)-1]
combined = combined.set_index('index')
new_index = pd.Index(np.arange(0,max_length+1,1))

combined = combined.reindex(new_index).reset_index()
combined = (combined.drop(['index'],axis=1))
nan_index = pd.isnull(combined).any(1).nonzero()[0]

for i in nan_index:
	splitted = get_english_words_out_of_string(df['test'][i])
	combined['test'][i] = splitted
print(combined)

