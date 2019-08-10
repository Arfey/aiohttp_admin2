SIMPLE_INPUT_TEMPALTE = '''
<div class="input-group mb-3">
  <div class="input-group-prepend">
    <span class="input-group-text"> {name} </span>
  </div>
  <input type="{type}" name="{name}" value="{value}" {required}>
</div>
{errors}
<br/>

'''

ERROR = '''
<p class='error'>{}</p>
'''