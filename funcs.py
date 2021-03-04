def sync_source_item(source, fetched, item):
    if isinstance(getattr(source, item), str) and item in fetched.keys():
        if getattr(source, item) == fetched[item]:
            return False    # no need to sync
        else:
            setattr(source, item, fetched[item])
            source.save()
            return True     # synced
    elif getattr(source, item) == None and item in fetched.keys():
        setattr(source, item, fetched[item])
        source.save()
        return True         # synced
    else:
        return False        # no need to sync