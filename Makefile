
RM	:= rm -rf

SRC_DIR := ./data/raw
OBJ_DIR := ./data/objs

SRC = $(shell find $(SRC_DIR)/ -type f -name '*.v' 2>/dev/null)
OBJ = $(patsubst $(SRC_DIR)/%.v, $(OBJ_DIR)/%.vo, $(SRC))

DATASET_AGGREGATED = $(PWD)/data/agg.csv

all:  $(OBJ)

$(DATASET_AGGREGATED): $(OBJ)
	python3 utils/aggregate.py -o $(DATASET_AGGREGATED)

preprocess: $(DATASET_AGGREGATED)

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
		data/agg.csv \
		data/test.csv \
		data/train.csv

clean_downloads:
	$(RM) \
		data/raw

# Delete all generated datas, leaving a clean repository
fclean: clean clean_downloads

.PHONY: \
	clean \
	fclean \
	clean_downloads \
	install \
	download \
	preprocess
