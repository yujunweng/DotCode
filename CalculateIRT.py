from pymongo import MongoClient
import numpy as np
import pandas as pd
import traceback
import os
import time
import datetime
import gc
from builtins import range
from numpy import (abs, array, concatenate, copy, exp, inf, log, log1p, max, newaxis, sort, sum)
from scipy.optimize import minimize
from scipy.stats import dirichlet, lognorm, norm
from scipy.special import expit





__all__ = ['two_parameter_model', 'four_parameter_model', 'estimate_thetas']

# Scale parameters for the a-priory distribution of parameters - 標度參數用於參數的先驗分佈
# The standard deviation of theta (student ability)
THETA_SCALE = 1.
# The standard deviation of log(a) (item discrimination)
A_SCALE = 1.7
# The standard deviation of b (item difficulty)
B_SCALE = 1.
# the alpha parameter for the Dirichlet distribution from which c and d
# are generated - the tuple returned is (pseudo-guessing probability, - 偽猜測概率
# inattention probability, 1 - the sum of both those probabilities)
C_D_DIRICHLET_ALPHA = (5, 5, 46)

# Parameters are initialized as the avg. of a large number of parameters
# which are randomly generated, how large should this number be?
INITIAL_PARAMETER_AVG = 100

# When scipy.optimize minimization fails with these messages, we can
# expect the result reached to still be pretty good
OPTIMIZE_MAX_REACHED_MSG = ['Maximum number of iterations has been exceeded.',
							'Maximum number of function evaluations '
							'has been exceeded.']
# Method parameter for scipy.optimize.minimize
MINIMIZATION_METHOD = 'Nelder-Mead'

# Bound on the number of MLE iterations
MAX_ITER = 100
# If no parameters has changed by more than DIFF in the last SMALL_DIFF_STREAK
# iterations, then we terminate the optimization process
DIFF = 0.001
SMALL_DIFF_STREAK = 3

def clientDB(database):
	client = MongoClient('localhost', 27017)
	db = client[database]
	return db

def clientCT(database, collection):
	ct = clientDB(database)[collection]
	return ct
			
def columnFunc(j, k, num):
	kList = []
	for i in range(j,k):
		kList.append(num)    
	return kList 
	
	
def scale_guessing(value, c, d):
	"""
	scale 2PL probability to fit the 4PL model.
	
	Accounts for the pseudo-guessing and inattention parameters given
	by `c` and `d`.
	"""
	return c + (d - c) * value

def rasch_model(b, theta):
	return expit( theta + array(b)) 


def two_parameter_model(a, b, theta):
	"""
	Estimate the likelihood of ability theta in a 2PL model.
	
	Apply the two-parameter logistic model with parameters `a` and `b`
	to estimate the likelihood of having ability `theta`.
	
	Parameters
	----------
	a : array_like
		Item discrimination, determines how sharp the rise in difficulty
		is, and controls the maximum slope of the probability curve,
		which is given by a / 4.
	b : array_like
		Item difficulty, controls the `theta` value which yields
		the maximal slope, which is given by ``-b / a``
	theta: array_like
		Student ability, the ability which we want to measure likelihood
		for.
	
	Returns
	-------
	p : array_like
		The probability of the given `theta` in the 2PL model
	
	Notes
	-----
	The 2PL likelihood function is given here by
	``LOGISTIC(a * x + b)``.
	This is a slightly different parametrization than what is given in
	most of the literature, which is ``LOGISTIC(a * (x - b))``.
	Here, ``LOGISTIC(x) = 1 / (1 + exp(-x))``.
	
	I've seen this different parametrization being referred to, in
	various sources, as ``(a*, b*)``, and also as ``(theta, lambda)``.
	Here the notation of ``(a, b)`` is kept for simplicity, despite the
	different meaning, as this parametrization is essentially equivalent
	and is better suited for faster and more stable convergence.
	
	If all inputs are numbers, then the returned result is the number
	representing the probability. If they are all arrays of the same
	shape, then the an array is returned, with a single entry
	corresponding to every ``(a, b, theta)`` entry in the input.
	If `a` and `b` are numbers but `theta` is an array, the probability
	is calculated for each theta, using the constant `a` and `b` given.
	
	"""
	return expit(a * theta + array(b))
	
	
def four_parameter_model(a, b, c, d, theta):
	"""
	Estimate the likelihood of ability theta in a 4PL model.
	
	Apply the four-parameter logistic model with parameters `a`, `b`,
	`c` and `d` to estimate the likelihood of having ability `theta`.
	
	Parameters
	----------
	a : array_like
		Item discrimination, determines how sharp the rise in difficulty
		is, and controls the maximum slope of the probability curve,
		which is given by a (d - c) / 4.
	b : array_like
		Item difficulty, controls the `theta` value which yields
		the maximal slope, which is given by ``-b / a``
	theta: array_like
	c : array_like
		The pseudo-guessing probability, the minimal chance of success
		when the ability decreases to negative infinity.
	d : array_like
		One minus the inattention probability, or alternatively the
		maximal chance of success when the ability increases to positive
		infinity.
	theta: array_like
		Student ability, the ability which we want to measure likelihood
		for.
	
	Returns
	-------
	p : array_like
		The probability of the given `theta` in the 4PL model
	
	Notes
	-----
	The 4PL likelihood function is given here by
	``c + (d - c) * LOGISTIC(a * x + b)``.
	This is a slightly different parametrization than what is given in
	most of the literature, which is
	``c + (d - c) * LOGISTIC(a * (x - b))``.
	Here, ``LOGISTIC(x) = 1 / (1 + exp(-x))``.
	
	I've seen this different parametrization being referred to, in
	various sources, as ``(a*, b*, c, d)``, and also as
	``(theta, lambda, c, d)``. Here the notation of ``(a, b, c, d)`` is
	kept for simplicity, despite the different meaning, as this
	parametrization is essentially equivalent and is better suited for
	faster and more stable convergence.
	
	If all inputs are numbers, then the returned result is the number
	representing the probability. If they are all arrays of the same
	shape, then the an array is returned, with a single entry
	corresponding to every ``(a, b, c, d, theta)`` entry in the input.
	If `a`, `b`, `c` and `d` are numbers but `theta` is an array, the
	probability  is calculated for each theta, using the constant `a`,
	`b`, `c` and `d` given.
	
	"""
	return scale_guessing(two_parameter_model(a, b, theta), c, d)


class StudentParametersDistribution(object):
	"""
	An object for generation and calculation of student parameters.
	"""
	def __init__(self, theta_scale=THETA_SCALE):	# THETA_SCALE = 1
		# norm是一個產生器, loc是平均值, scale是標準差
		self.theta = norm(loc=0., scale=theta_scale)	
		print("theta=", self.theta)
	
	def rvs(self, size=None):
		# return 常態分佈的隨機變數 (random variable), 隨機變數的數量是size 
		print("StudentParametersDistribution.rvs.size=", size)
		print("length of theta.rvs=", len(self.theta.rvs(size)))
		return self.theta.rvs(size)
	
	def logpdf(self, theta):
		# 回傳norm(0, 1).logpdf
		qq = self.theta.logpdf(theta)
		#print(" logpdf=", qq)
		return qq


class QuestionParametersDistribution(object):
	"""
	An object for generation and calculation of question parameters.
	"""
	# A_SCALE The standard deviation of log(a) (item discrimination) a = 1.7
	# B_SCALE The standard deviation of b (item difficulty) b = 1.
	def __init__(self, a_scale=A_SCALE, b_scale=B_SCALE,
				c_d_dirichlet_alpha=C_D_DIRICHLET_ALPHA):
		self.a = lognorm(s=1., scale=a_scale)
		self.b = norm(scale=b_scale)
		self.c_d = dirichlet(alpha=c_d_dirichlet_alpha)
	
	def rvs(self, size=None):
		a = self.a.rvs(size)
		b = self.b.rvs(size)
		c_d = self.c_d.rvs(size)
		c = c_d[..., 0]
		d = 1 - c_d[..., 1]
		return concatenate((a[..., newaxis], b[..., newaxis],
							c[..., newaxis], d[..., newaxis]), axis=-1)
	
	def logpdf(self, a, b, c, d):
		return (self.a.logpdf(a) + self.b.logpdf(b) +
				self.c_d.logpdf([c, 1 - d, d - c]))


def learn_abcd(thetas, question_dist, corrects):
	"""
	Returns a function that can calculate the log-likelihood of question
	parameters given thetas and answers of different students.
	
	Returns an estimation function suitable for optimization.
	"""
	def f(arg):
		a, b, c, d = arg
		if a <= 0 or c < 0 or d > 1 or d - c < 0:
			# invalid parameters - return inf so minimization function
			# will learn to avoid it
			return inf
		mult = question_dist.logpdf(a, b, c, d)
		#p = four_parameter_model(a, b, c, d, thetas)
		#p = two_parameter_model(a, b, thetas)
		p = rasch_model(b, thetas)
		for i, correct in enumerate(corrects):
			# correct answer is 1, incorrect by -1, no answer is 0
			# multiply by a factor of 2 per student, to utilize log1p
			mult += log1p((2 * p[i] - 1) * correct)
		return -mult
	return f


def learn_theta(abcds, student_dist, corrects):
	"""
	Returns a function that can calculate the log-likelihood of student
	parameters given question parameters and answers of different
	students.
	
	Returns an estimation function suitable for optimization.
	"""
	def f(theta):
		theta = theta[0]
		mult = student_dist.logpdf(theta)
		a, b, c, d = abcds.T
		#p = four_parameter_model(a, b, c, d, theta)
		#p = two_parameter_model(a, b, theta)
		p = rasch_model(b, theta)
		for i, correct in enumerate(corrects):
			# correct answer is 1, incorrect by -1, no answer is 0
			# multiply by a factor of 2 per question, to utilize log1p
			mult += log1p((2 * p[i] - 1) * correct)
		return -mult
	return f


def expanded_scores(score_matrix):
	answers = [list(set(score)) for score in score_matrix]
	subscores = []
	for i, question_scores in enumerate(score_matrix):
		best = len(answers[i])
		subscores_per_student = []
		for student_score in question_scores:
			expanded = [1] * answers[i].index(student_score)
			if len(expanded) < best - 1:
				expanded = expanded + [-1]
				expanded = expanded + [0] * (best - 1 - len(expanded))
			subscores_per_student.append(expanded)
		subscores.append(array(subscores_per_student).T)
	return concatenate(subscores)


def initialize_random_values(students_count, subquestions_count,
							student_dist, question_dist):
	theta_values = sum(student_dist.rvs(size=(INITIAL_PARAMETER_AVG,
											students_count)),
					axis=0) / INITIAL_PARAMETER_AVG
	abcd_values = sum(question_dist.rvs(size=(INITIAL_PARAMETER_AVG,
											subquestions_count)),
					axis=0) / INITIAL_PARAMETER_AVG
	return theta_values, abcd_values


def initialize_estimation(scores, student_dist, question_dist):
	# Even though we usually input the table as scores per student,
	# the analysis is easier for a table of scores per question:
	scores = scores.T
	questions_count, students_count = scores.shape
	# Split each question into small sub-question.
	# 對每一個題目的答案取唯一值, 再對每個問題的答案進行排序
	answers_per_question = [sort(array(list(set(score))))
							for score in scores]
	# 計算每個問題的唯一答案值有幾個						
	subquestions_per_question = [len(answers)
								for answers in answers_per_question]
	# 把每個問題的唯一答案值數量加總, 再減去問題的數量, 不明白意義是什麼
	subquestions_count = sum(subquestions_per_question) - questions_count
	# Begin with small random values per parameter to break symmetry.
	thetas, abcds = initialize_random_values(students_count,
											subquestions_count,
											student_dist, question_dist)
	# Modify the question array according to those new sub-questions.
	expanded = expanded_scores(scores)
	return expanded, thetas, abcds


def parse_optimization_result(res):
	"""
	Modify the dictionary returned by scipy.optimize.minimize to get the
	actual optimal value of `x` obtained by the minimization process.
	"""
	if not res['success'] and res['message'] not in OPTIMIZE_MAX_REACHED_MSG:
		raise RuntimeError("Optimization failed:\n" + repr(res))
	return res['x']


def question_abcd_given_theta(thetas, question_dist, scores, initial_abcd):
	"""
	find the maximal-likelihood question parameters, given the ability
	and answers of all students, for a single question
	"""
	to_minimize = learn_abcd(thetas, question_dist, scores)
	res = minimize(to_minimize, initial_abcd, method=MINIMIZATION_METHOD)
	print("res=", res)
	return parse_optimization_result(res)


def all_abcds_given_theta(thetas, question_dist, scores, abcds):
	"""
	find the maximal-likelihood question parameters, given the ability
	and answers of all students, for all questions question
	"""
	print("len(abcds):", len(abcds))
	return array([question_abcd_given_theta(thetas, question_dist,
											scores[i], abcds[i])
				for i in range(len(abcds))])


def student_theta_given_abcd(abcds, student_dist, scores, inital_theta):
	"""
	find the maximal-likelihood ability parameter of a single student,
	given his answers and the parameters of the questions
	"""
	to_minimize = learn_theta(abcds, student_dist, scores)
	res = minimize(to_minimize, [inital_theta], method=MINIMIZATION_METHOD)
	return parse_optimization_result(res)


def all_thetas_given_abcd(abcds, student_dist, scores, thetas):
	"""
	find the maximal-likelihood ability parameter of a all students,
	given their answers and the parameters of the questions
	"""
	return array([student_theta_given_abcd(abcds, student_dist,
										scores[:, i], thetas[i])
				for i in range(len(thetas))])


def estimate_thetas(scores, verbose=False):
	"""
	Estimates the student theta (ability) and question parameters.
	
	Currently uses JMLE to simultaneously estimate the parameters for
	students and for questions.
	
	Parameters
	----------
	scores : array_like
		A 2-dimensional array of question scores, where each row
		corresponds to a single student. Grades should be integers but
		their scale can be arbitrary (supports partial credit, not only
		0 and 1).
	
	"""
	print("start student_dist...")
	student_dist = StudentParametersDistribution()
	print("start question_dist...")
	question_dist = QuestionParametersDistribution()
	print("start initialize_estimation...")
	expanded, thetas, abcds = initialize_estimation(scores, student_dist,
													question_dist)
	small_diffs_streak = 0
	iter_count = 0
	
	while iter_count < MAX_ITER and small_diffs_streak < SMALL_DIFF_STREAK:
		start = time.time()
		old_abcds, old_thetas = copy(abcds), copy(thetas)
		print("start all_abcds_given_theta...") #很久
		abcds = all_abcds_given_theta(thetas, question_dist, expanded, abcds)
		print("start all_thetas_given_abcd...")
		thetas = all_thetas_given_abcd(abcds, student_dist, expanded, thetas)
		# How much have the parameters changed from last time?
		diff = max([max(abs(old_abcds - abcds)),
					max(abs(old_thetas - thetas))])
		if diff < DIFF:	
			small_diffs_streak += 1
		else:	# 必須連續3次值小於0.001
			small_diffs_streak = 0
		iter_count += 1
		if verbose:
			print(diff)
		print(time.time()-start, "秒")	
	print('thetas:', thetas, "\n", 'abcds:', abcds)
	return thetas, abcds
	
	

if __name__ == '__main__':
	database = 'dotCode'
	db = clientDB(database)
	collection = 'Elo'		
	ct = clientCT(database, collection)
	db.Elo.create_index([('gameCode', 1), ('userId', 1), ('sectionId', 1)])
	
	maxId = 67900
	qualify_users = []
	for id in range(0, maxId): 
		for one in ct.find({"gameCode":"Duck", "userId":id}):
			if one['maxSection'] >= 8:
				for section in range(1, one['maxSection']+1):
					if ('section%d_elo' %section) not in one.keys():
						break
					if section == one['maxSection']:
						qualify_users.append(one['userId'])
						print(id)
						
						
	#qualify_users = np.array(qualify_users)
	print(len(qualify_users))
	s = input("press enter to continue...")
	
	print("start to create index...")
	collection = 'FirstRecord'		
	ct = clientCT(database, collection)
	ct.create_index([('gameCode', 1), ('userId', 1), ('sectionId', 1)])
	print("create index completed!")

	game = 'Duck'
	
	if game == 'Maze':
		maxSection = 40
	elif game == 'Duck':
		maxSection = 60	
	
	answersTable = []
	peo = 0
	for id in qualify_users: 
		id_exists = 0
		userAnswers = np.array(columnFunc(0, maxSection, 0))
		#print(id)
		for section in range(1, maxSection+1):
			for one in ct.find({"gameCode":game, "userId":id, "sectionId":section}):
				if one['gameStar'] == 0:
					userAnswers[section-1] = -1
				elif one['gameStar'] == 1:	
					userAnswers[section-1] = 1/3
				elif one['gameStar'] == 2:	
					userAnswers[section-1] = 2/3
				elif one['gameStar'] == 3:	
					userAnswers[section-1] = 1
				elif one['gameStar'] == 4:
					userAnswers[section-1] = 4/3
				else:
					userAnswers[section-1] = 0
				id_exists = 1
		if id_exists:		
			#print(userAnswers)
			#s = input("")
			answersTable.append(userAnswers)
		peo += id_exists			
	answersTable = np.array(answersTable)
	print("shape:", answersTable.shape)
	#print(answersTable)
	result_thetas, result_abcds = estimate_thetas(answersTable, verbose=True)
	db.FirstRecord.update_one
	
	
	print("peo:", peo, len(result_thetas), len(result_abcds))
	
