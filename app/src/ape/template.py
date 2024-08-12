class GenerationTemplate:
    """
    Takes a prompt template and provides methods for filling in blanks.
    The format is as follows:
    [APE] is where text will be generated by the LLM.
    [full_DEMO] is where the full demo will be inserted.
    [INPUT] is where the input to the first demo will be inserted.
    [OUTPUT] is where the output from the first demo will be inserted.
    """

    def __init__(self, template):
        self.template = template
        # Check that the template is valid
        # There should be exactly one [APE] token
        assert self.template.count('[APE]') == 1

    def fill(self, full_demo='', input='', output=''):
        """
        Fills in the template with the given values.
        """
        return self.template.replace('[full_DEMO]', full_demo).replace(
            '[INPUT]', input).replace('[OUTPUT]', output)


class EvalTemplate:
    """
    Takes a prompt template and provides methods for filling in blanks.
    The format is as follows:
    [PROMPT] is where the prompt will be inserted.
    [full_DEMO] is where the full demo will be inserted.
    [INPUT] is where the input to the first demo will be inserted.
    [OUTPUT] is where the output from the first demo will be inserted.
    """

    def __init__(self, template):
        self.template = template

    def fill(self, prompt='', full_demo='', input='', output=''):
        """
        Fills in the template with the given values.
        """
        return self.template.replace('[PROMPT]', prompt).replace(
            '[full_DEMO]', full_demo).replace('[INPUT]', input).replace('[OUTPUT]', output)

    def convert_to_generation_template(self):
        """
        Converts the evaluation template to a generation template.
        """
        return GenerationTemplate(self.template.replace('[PROMPT]', '[APE]'))


class DemosTemplate:
    """
    Takes a template for the full demo and provides methods for filling in blanks.
    The format is as follows:
    [INPUT], [OUTPUT]

    """

    def __init__(self, template, delimiter='\n\n'):
        self.template = template
        self.delimiter = delimiter

    def fill(self, data):
        """
        Fills in the template with the given values. Data is a tuple of lists.
        """
        demos = ''
        for i, (input_, output_) in enumerate(zip(*data)):
            demos += self.template.replace('[INPUT]', input_).replace(
                '[OUTPUT]', output_)

            if i != len(data[0]) - 1:
                demos += self.delimiter

        return demos
