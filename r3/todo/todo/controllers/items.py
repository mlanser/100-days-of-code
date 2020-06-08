from cement import Controller, ex


class Items(Controller):
    class Meta:
        label = 'items'
        stacked_type = 'embedded'
        stacked_on = 'base'
    
    @ex(help='list items')
    def list(self):
        pass
        
    @ex(help='create new item')
    def create(self):
        pass
        
    @ex(help='update an existing item')
    def update(self):
        pass
    
    @ex(help='delete an item')
    def delete(self):
        pass
    
    @ex(help='complete an item')
    def complete(self):
        pass
        