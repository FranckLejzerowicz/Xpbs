# ----------------------------------------------------------------------------
# Copyright (c) 2020, Franck Lejzerowicz.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------


def chunks(l, chunk_size, chunk_number=0):
	# Adapted from:
	# https://stackoverflow.com/questions/312443/how-do-you-split-a-list-into-evenly-sized-chunks
	if chunk_size:
		return [l[i:i + chunk_size] for i in range(0, len(l), chunk_size)]
	else:
		n = len(l)//chunk_number
		return [l[i:i + n] for i in range(0, len(l), n)]
