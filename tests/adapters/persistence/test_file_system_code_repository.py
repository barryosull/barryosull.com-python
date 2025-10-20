import tempfile
from pathlib import Path
from uuid import uuid4

import pytest

from src.adapters.persistence.file_system_code_repository import (
    FileSystemCodeRepository,
)


@pytest.fixture
def temp_dir():
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


@pytest.fixture
def repository(temp_dir):
    return FileSystemCodeRepository(base_path=temp_dir)


def test_files_are_created(temp_dir, repository):
    room_id = uuid4()
    repository.generate_code_for_room(room_id)

    counter_file = Path(temp_dir) / "code_counter.json"
    mappings_file = Path(temp_dir) / "code_mappings.json"

    assert counter_file.exists()
    assert mappings_file.exists()


def test_persistence_across_repository_instances(temp_dir):
    room_id = uuid4()

    repo1 = FileSystemCodeRepository(base_path=temp_dir)
    code = repo1.generate_code_for_room(room_id)

    repo2 = FileSystemCodeRepository(base_path=temp_dir)
    found_room_id = repo2.find_room_by_code(code)

    assert found_room_id == room_id


def test_counter_persists_across_instances(temp_dir):
    repo1 = FileSystemCodeRepository(base_path=temp_dir)
    room1_id = uuid4()
    room2_id = uuid4()

    code1 = repo1.generate_code_for_room(room1_id)

    repo2 = FileSystemCodeRepository(base_path=temp_dir)
    code2 = repo2.generate_code_for_room(room2_id)

    assert code1 == "QGLJ"
    assert code2 == "GX72"