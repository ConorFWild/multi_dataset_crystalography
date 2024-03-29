import cctbx


from dataset.dataset import PanddaDataset
from structure.align import align_structures_flexible


# Path -> str
def get_dtag_from_path(path):
    return path.parent.name


# Path x Path -> PanDDADataset
def load_dataset(pdb_path, mtz_path, num=0):
    dtag = get_dtag_from_path(pdb_path)
    dataset = PanddaDataset.from_file(model_filename=str(pdb_path),
                            data_filename=str(mtz_path))
    dataset.label(num=num, tag=dtag)

    return dataset


# PanddaDatset -> flex_array
def load_xmap_from_pandda_dataset(pandda_dataset, min_res=0, dataset_sfs='FWT,PHWT'):

    try:
        miller_array = pandda_dataset.data.miller_arrays['truncated']
    except Exception as e:
        ma_unscaled_com = pandda_dataset.data.get_structure_factors(columns=dataset_sfs)
        # Store in the dataset object
        pandda_dataset.data.miller_arrays[dataset_sfs] = ma_unscaled_com
        miller_array = pandda_dataset.data.miller_arrays[dataset_sfs]

    # FFT
    flex_ed_map = miller_array.fft_map(
        resolution_factor=0.25,
        d_min=min_res,
        symmetry_flags=cctbx.maptbx.use_space_group_symmetry)

    scaled_map = flex_ed_map.apply_sigma_scaling().real_map()

    return scaled_map


# hierarchy{reference} x hierarchy{move} x (hierarchy{reference} -> hierarchy{move} -> alignments)
def align_structures(reference_structure, structure, alignment_method=align_structures_flexible):

    multiple_local_alignment = alignment_method(structure, reference_structure)

    return multiple_local_alignment