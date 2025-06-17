To regenerate Python lexer and parser sources following grammar changes, obtain the ANTLR4 tool from [here](https://www.antlr.org/download/antlr-4.13.2-complete.jar), and run it as follows:

```
java -jar \path\to\antlr-4.13.2-complete.jar -Dlanguage=Python3 -visitor grammar_file.g4
```

Note that you will need to install Java to run ANTLR4.
