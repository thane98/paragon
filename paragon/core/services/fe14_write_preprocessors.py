import logging

from paragon.core.services.write_preprocessors import WritePreprocessors


class FE14WritePreprocessors(WritePreprocessors):
    def invoke(self, gd):
        self.assign_support_ids_and_validate_tables(gd)

    @staticmethod
    def assign_support_ids_and_validate_tables(gd):
        # Get info on support and character tables.
        support_table_info = gd.table("supports")
        char_table_info = gd.table("characters")
        if not support_table_info or not char_table_info:
            logging.error("Could not assign support IDs due to missing table info.")
            return
        support_table_rid, support_table_field_id = support_table_info
        char_table_rid, char_table_field_id = char_table_info

        # Ensure that all tables contain valid characters.
        tables = gd.items(support_table_rid, support_table_field_id)
        for i in range(0, len(tables)):
            # Read the support table's pointer.
            table_pointer = tables[i]
            table_rid = gd.rid(table_pointer, "table")
            if not table_rid:
                # Bad entry. Let's clean this up.
                gd.list_remove(support_table_rid, support_table_field_id, i)
                logging.debug("Removed bad support table at index " + str(i))
                continue

            # Get the owner of the table.
            owner = gd.rid(table_rid, "owner")
            if not owner:
                # Also a bad table. Get rid of it.
                gd.list_remove(support_table_rid, support_table_field_id, i)
                logging.debug("Removed bad support table at index " + str(i))
                continue

            # Make sure the owner is still in the character table.
            index = gd.list_index_of(char_table_rid, char_table_field_id, owner)
            if not index:
                # Not present, so this support table is useless.
                gd.list_remove(support_table_rid, support_table_field_id, i)
                logging.debug("Removed bad support table at index " + str(i))
                continue

        # Now go through and assign support IDs
        tables = gd.items(support_table_rid, support_table_field_id)
        next_support_id = 0
        for table_pointer in tables:
            table_rid = gd.rid(table_pointer, "table")
            owner = gd.rid(table_rid, "owner")
            gd.set_int(owner, "support_id", next_support_id)
            logging.debug(f"Gave support id {next_support_id} to character {gd.display(owner)}.")
            next_support_id += 1
