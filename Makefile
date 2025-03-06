all: petition.pdf

petition.pdf: petition.tex
	pdflatex petition.tex

clean:
	rm -f *.aux *.log *.out *.toc petition.pdf

view: petition.pdf
	@case "$$(uname)" in \
		Darwin) open petition.pdf ;; \
		Linux) xdg-open petition.pdf || gio open petition.pdf ;; \
		CYGWIN*|MINGW32*|MSYS*|MINGW*) cygstart petition.pdf || start petition.pdf ;; \
		*) echo "Unsupported OS"; exit 1 ;; \
	esac
