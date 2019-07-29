SIMPLE_INPUT_TEMPALTE = '''
<label>
    {name}
    <input type="{type}" name="{name}" value="{value}" {required}>
</label>
{errors}
<br/>
'''

ERROR = '''
<p class='error'>{}</p>
'''