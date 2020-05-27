# shipping.py

import iso6346
from itertools import chain

class ShippingContainer:
    
    next_serial = 1337
    some_counter = 0
    
    @staticmethod                                                   # Use '@staticmethod' when we don't need to refer to
    def _add_prefix(item):                                          # the class object
        if item == None:
            return None
        
        items = []
        if isinstance(item, str) or isinstance(item, int):
            items.append(item)
        else:
            items += item

        return list(chain("Lots of {}".format(str(x)) for x in items if x != None))

    
    @classmethod                                                    # Use '@classmethod' when we need to refer to
    def _get_next_serial(cls):                                      # the class object like we do
        result = cls.next_serial                                    # <--   ... here ...
        cls.next_serial += 1                                        # <--   ... and here
        return result
    
    
    @staticmethod
    def _make_bic_code(owner_code, serial):
        return iso6346.create(owner_code=owner_code, serial=str(serial).zfill(6))

    
    @classmethod
    def create_empty(cls, owner_code):
        return cls(owner_code, contents=None)
    
    
    @classmethod
    def create_with_items(cls, owner_code, items):
        #return cls(owner_code, contents=list(items))
        return cls(owner_code, items)


    def __init__(self, owner_code, contents):
        self.contents = ShippingContainer._add_prefix(contents)
        self.bic = self._make_bic_code(                             # Using 'self' to ensure that we're calling instance 
            owner_code=owner_code,                                  # version of method in inherited classes
            serial=ShippingContainer._get_next_serial())

        

        
        
class RefrigeratedShippingContainer(ShippingContainer):
    @staticmethod
    def _make_bic_code(owner_code, serial):
        return iso6346.create(owner_code=owner_code,
                              serial=str(serial).zfill(6),
                              category='R')
    
    