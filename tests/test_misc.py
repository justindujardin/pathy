from pathlib import Path

import pytest

import spacy
from gcspath import GCSPath, use_fs


def test_export_spacy_model(temp_folder):
    use_fs(temp_folder)
    bucket = GCSPath("/my-bucket/")
    bucket.mkdir(exist_ok=True)
    model = spacy.blank("en")
    output_path = GCSPath("/my-bucket/models/my_model")
    model.to_disk(output_path)
    sorted_entries = sorted([str(p) for p in output_path.glob("*")])
    expected_entries = [
        "/my-bucket/models/my_model/meta.json",
        "/my-bucket/models/my_model/tokenizer",
        "/my-bucket/models/my_model/vocab",
    ]
    assert sorted_entries == expected_entries
