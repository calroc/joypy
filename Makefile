clean:
	$(RM) -r Joypy.egg-info/ dist/
	find . -name '*.pyc' | xargs $(RM)
