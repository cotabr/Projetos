banco = list.files(pattern = "\\.rmd$")

#ex1 <- exams2nops(banco, language = "pt-BR", title="Lista 1", 
#                  institution = "Universidade Federal do Pará", 
#                  course = "Análise de Sistemas Lineares",n=2)

ex1 <- exams2html(banco, mathjax = TRUE)