"""
Unit tests for WriteBarrier.

Tests the write barrier that records cross-generational pointers
when old generation objects reference young generation objects.
"""

import pytest


class TestWriteBarrierInit:
    """Test WriteBarrier initialization."""

    def test_create_write_barrier(self):
        """
        Given no existing remembered set
        When WriteBarrier is created
        Then it should initialize with a remembered set
        """
        from components.generational_gc.src.write_barrier import WriteBarrier

        wb = WriteBarrier()

        assert wb.remembered_set is not None
        assert len(wb.remembered_set) == 0


class TestWriteBarrierRecordPointer:
    """Test recording cross-generational pointers."""

    def test_record_old_to_young_pointer(self):
        """
        Given a write barrier
        When recording an old→young pointer
        Then it should be added to remembered set
        """
        from components.generational_gc.src.write_barrier import WriteBarrier

        wb = WriteBarrier()
        old_ptr = 1000
        young_ptr = 500

        wb.record_pointer(from_ptr=old_ptr, to_ptr=young_ptr)

        assert wb.remembered_set.contains(old_ptr) is True

    def test_record_multiple_pointers(self):
        """
        Given a write barrier
        When recording multiple old→young pointers
        Then all should be in remembered set
        """
        from components.generational_gc.src.write_barrier import WriteBarrier

        wb = WriteBarrier()

        wb.record_pointer(from_ptr=1000, to_ptr=500)
        wb.record_pointer(from_ptr=2000, to_ptr=600)
        wb.record_pointer(from_ptr=3000, to_ptr=700)

        assert len(wb.remembered_set) == 3


class TestWriteBarrierExecute:
    """Test executing write barrier on store."""

    def test_execute_old_to_young_store(self):
        """
        Given old and young generation objects
        When executing write barrier for old→young store
        Then pointer should be recorded
        """
        from components.generational_gc.src.write_barrier import WriteBarrier

        wb = WriteBarrier()
        old_ptr = 1000
        young_ptr = 500

        wb.execute(obj_ptr=old_ptr, field_offset=0, value=young_ptr,
                   is_old_gen=True, is_value_young=True)

        assert wb.remembered_set.contains(old_ptr) is True

    def test_execute_old_to_old_store(self):
        """
        Given old generation objects
        When executing write barrier for old→old store
        Then pointer should NOT be recorded
        """
        from components.generational_gc.src.write_barrier import WriteBarrier

        wb = WriteBarrier()
        old_ptr1 = 1000
        old_ptr2 = 2000

        wb.execute(obj_ptr=old_ptr1, field_offset=0, value=old_ptr2,
                   is_old_gen=True, is_value_young=False)

        assert len(wb.remembered_set) == 0

    def test_execute_young_to_young_store(self):
        """
        Given young generation objects
        When executing write barrier for young→young store
        Then pointer should NOT be recorded
        """
        from components.generational_gc.src.write_barrier import WriteBarrier

        wb = WriteBarrier()
        young_ptr1 = 500
        young_ptr2 = 600

        wb.execute(obj_ptr=young_ptr1, field_offset=0, value=young_ptr2,
                   is_old_gen=False, is_value_young=True)

        assert len(wb.remembered_set) == 0


class TestWriteBarrierClear:
    """Test clearing remembered set."""

    def test_clear_after_minor_gc(self):
        """
        Given write barrier with recorded pointers
        When clearing after minor GC
        Then remembered set should be empty
        """
        from components.generational_gc.src.write_barrier import WriteBarrier

        wb = WriteBarrier()

        wb.record_pointer(from_ptr=1000, to_ptr=500)
        wb.record_pointer(from_ptr=2000, to_ptr=600)

        wb.clear()

        assert len(wb.remembered_set) == 0


class TestWriteBarrierGetRememberedPointers:
    """Test getting remembered pointers."""

    def test_get_pointers(self):
        """
        Given write barrier with recorded pointers
        When getting remembered pointers
        Then all should be returned
        """
        from components.generational_gc.src.write_barrier import WriteBarrier

        wb = WriteBarrier()

        wb.record_pointer(from_ptr=1000, to_ptr=500)
        wb.record_pointer(from_ptr=2000, to_ptr=600)

        pointers = list(wb.get_remembered_pointers())

        assert len(pointers) == 2
        assert 1000 in pointers
        assert 2000 in pointers
