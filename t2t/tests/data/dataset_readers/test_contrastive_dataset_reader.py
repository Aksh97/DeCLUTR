import pytest
from hypothesis import given, settings
from hypothesis.strategies import integers, text

from t2t.data.dataset_readers import ContrastiveDatasetReader


class TestContrastiveDatasetReader:
    # Not clear why turning off the deadline is neccesary? Errors out otherwise.
    @settings(deadline=None)
    @given(num_spans=integers(min_value=0, max_value=1))
    def test_no_sample_context_manager(self, num_spans: int):
        dataset_reader = ContrastiveDatasetReader(
            num_spans=num_spans, max_span_len=32, min_span_len=16
        )

        # While in the scope of the context manager, sample_spans should be false.
        # After existing the context manger, it should return to whatever value it was at
        # before entering the contxt manager.
        previous = dataset_reader.sample_spans
        with dataset_reader.no_sample():
            assert not dataset_reader.sample_spans
        assert dataset_reader.sample_spans == previous

    @given(
        num_spans=integers(min_value=0, max_value=2),
        max_span_len=integers(min_value=16, max_value=32),
        min_span_len=integers(min_value=16, max_value=32),
    )
    def test_init_raises_value_error_no_max_min_span_length(
        self, num_spans: int, max_span_len: int, min_span_len: int
    ):
        if num_spans:  # should only raise the error when num_spans is truthy
            with pytest.raises(ValueError):
                _ = ContrastiveDatasetReader(
                    num_spans=num_spans, max_span_len=None, min_span_len=min_span_len
                )
            with pytest.raises(ValueError):
                _ = ContrastiveDatasetReader(
                    num_spans=num_spans, max_span_len=max_span_len, min_span_len=None
                )
            with pytest.raises(ValueError):
                _ = ContrastiveDatasetReader(
                    num_spans=num_spans, max_span_len=None, min_span_len=None
                )

    @given(
        num_spans=integers(min_value=0, max_value=2),
        max_span_len=integers(min_value=16, max_value=32),
        min_span_len=integers(min_value=16, max_value=32),
        sampling_strategy=text(),
    )
    def test_init_raises_value_error_invalid_sampling_strategy(
        self, num_spans: int, max_span_len: int, min_span_len: int, sampling_strategy: str
    ):
        if num_spans:  # should only raise the error when num_spans is truthy
            with pytest.raises(ValueError):
                _ = ContrastiveDatasetReader(
                    num_spans=num_spans,
                    max_span_len=max_span_len,
                    min_span_len=min_span_len,
                    sampling_strategy=sampling_strategy,
                )