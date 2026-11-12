VB = 'https://visionbook.mit.edu/'
def L(slug, txt): return f'<a href="{VB}{slug}" target="_blank">{txt}</a>'
LK = {
 '{C51}': L('VLMs.html', 'cap. 51'),
 '{C30}': L('representation_learning.html', 'cap. 30'),
 '{C26}': L('transformers.html', 'cap. 26'),
 '{C32}': L('generative_models.html', 'cap. 32'),
 '{C34}': L('conditional_generative_models.html', 'cap. 34'),
 '{C37}': L('transfer_learning.html', 'cap. 37'),
 '{C13}': L('neural_nets_as_distribution_transformers.html', 'cap. 13'),
 '{C50}': L('object_recognition_v3.html', 'cap. 50'),
}
def P(n): return f' <em>· pag. {n}/61</em>'
def R(t):
    for k, v in LK.items(): t = t.replace(k, v)
    return t
