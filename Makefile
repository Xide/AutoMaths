RM	:= rm -rf

SRC_DIR := $(PWD)/data/raw
OBJ_DIR := $(PWD)/data/objs

SRC = $(shell find $(SRC_DIR)/ -type f -name '*.v' 2>/dev/null)
OBJ = $(patsubst $(SRC_DIR)/%.v, $(OBJ_DIR)/%.vo, $(SRC))

DATASET_AGGREGATED = $(PWD)/data/agg.csv
DATASET_CLEANED = $(PWD)/data/clean.csv

$(DATASET_CLEANED): $(DATASET_AGGREGATED)
	python3 srcs/preprocess/clean_dataset.py -i $(DATASET_AGGREGATED) -o $(DATASET_CLEANED)

$(DATASET_AGGREGATED): $(SRC_DIR) $(OBJ)
	python3 srcs/preprocess/aggregate.py -s $(OBJ_DIR) -o $(DATASET_AGGREGATED)

$(SRC_DIR):
		./data/download.sh $(SRC_DIR)

$(OBJ_DIR)/%.vo: $(SRC_DIR)/%.v
	@mkdir -p "$(@D)"
	python3 srcs/preprocess/preprocess.py "$<" -o "$@"

all: preprocess

preprocess: $(DATASET_CLEANED)

install:
	pip install -r requirements.txt --user

# Delete preprocessing and rnutime generated datas
clean:
	$(RM) \
		data/objs \
		data/runs \
		data/agg.csv \
		data/clean.csv \
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
	preprocess
