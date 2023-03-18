CC = gcc

BLDDIR = build
BINDIR = bin
SRCDIR = src



all: $(BINDIR)/read_msr

$(BLDDIR)/%.o: $(SRCDIR)/rd-msr/%.c
	$(CC) -c $< -o $@

$(BINDIR)/read_msr: $(BLDDIR)/read_msr.o
	$(CC) $^ -o $@

.PHONY: clean

clean:
	rm -f $(BLDDIR)/*.o $(BINDIR)/*
