
RM	:= rm -rf

SRC_DIR := ./data/raw
OBJ_DIR := ./data/objs

SRC = $(shell find $(SRC_DIR)/ -type f -name '*.v' 2>/dev/null)
OBJ = $(patsubst $(SRC_DIR)/%.v, $(OBJ_DIR)/%.vo, $(SRC))

all:  $(OBJ)

download:
		./data/download.sh $(SRC_DIR)


$(OBJ_DIR)/%.vo: $(SRC_DIR)/%.v
	@mkdir -p "$(@D)"
	python3 utils/preprocess.py "$<" -o "$@"

install:
	pip install -r requirements.txt


# Delete preprocessing and rnutime generated datas
clean:
	$(RM) \
		data/objs \
		data/runs \
		data/test.csv \
		data/train.csv

clean_downloads:
	$(RM) \
		data/raw

# Delete all generated datas, leaving a clean repository
fclean: clean clean_downloads
