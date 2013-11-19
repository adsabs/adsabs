from .views import buggyme_blueprint as blueprint, is_message_dismissed
from flask import flash, session, g, get_flashed_messages
from adsabs.core import set_global_messages, get_global_messages

def setup(app):
    
    # register a context processor that will be called with each request
    # we'll add flash messages to every page (unless the message has 
    # been already seen and dismissed by the user)        
    def new_context_processor():
        
        # this sucks because there is not a way (that i know off) to 
        # dynamically register data/messages; and saving the message
        # into a text file is the same as saving it here. As far as I 
        # can tell, there is no permanent storage available to 
        # blueprints (yes, exactly, this is the argument in the discussion
        # between Django and Flask)
        msg = None
        cat = 'html'
        if msg and not is_message_dismissed(msg, cat):
            
            set_global_messages(
                """
                $(document).ready(function() {
                      $('div#globalmsg').find('button.close').click(
                     function(){
                        $.get('./buggyme/',{msg: $(this).parent().find('span').html(), });
                     });
                });""", 'javascript');
                
            safe_to_add = True
            # this results in messages be displayed every other request:
            #for existing_category, existing_msg in get_flashed_messages(with_categories=True):
            #    if existing_msg == msg:
            #         safe_to_add = False
            #         break
            if safe_to_add:
                #flash(msg, cat)
                set_global_messages(msg, cat)
            
            
        return {}
    
    app.template_context_processors[None].append(new_context_processor)
