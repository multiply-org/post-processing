from multiply_post_processing.functional_diversity_metrics_post_processor import \
    CVHFunction, FDIVFunction, FEFunction, MNNDFunction, FunctionalDiversityMetricsPostProcessor, _pre_process, \
    _pre_process_trait, _process
import numpy as np
from pytest import approx

__author__ = "Tonio Fincke (Brockmann Consult GmbH)"


def test_get_num_time_steps():
    assert 1 == FunctionalDiversityMetricsPostProcessor.get_num_time_steps()


def test_get_names_of_required_variables():
    names_of_required_variables = FunctionalDiversityMetricsPostProcessor.get_names_of_required_variables()
    assert names_of_required_variables is not None
    assert 3 == len(names_of_required_variables)
    assert 'lai' in names_of_required_variables
    assert 'cab' in names_of_required_variables
    assert 'cw' in names_of_required_variables


def test_get_name():
    assert 'FunctionalDiversityMetrics' == FunctionalDiversityMetricsPostProcessor.get_name()


# def test_get_indicator_descriptions():
#     indicator_descriptions = FunctionalDiversityMetricsPostProcessor.get_indicator_descriptions()


def test_pre_process():
    lai = np.array([0.0, 1.0, 2.0, 3.0])
    cab = np.array([1.0, 0.0, 2.0, 3.0])
    cw = np.array([2.0, 1.0, 0.0, 3.0])
    (a_lai, a_cab, a_cw) = _pre_process(lai, cab, cw)

    sqrt_1_5 = np.sqrt(1.5)

    assert np.isnan(a_lai[0])
    assert approx(-sqrt_1_5) == a_lai[1]
    assert approx(0.0) == a_lai[2]
    assert approx(sqrt_1_5) == a_lai[3]
    assert approx(-sqrt_1_5) == a_cab[0]
    assert np.isnan(a_cab[1])
    assert approx(0.0) == a_cab[2]
    assert approx(sqrt_1_5) == a_cab[3]
    assert approx(0.0) == a_cw[0]
    assert approx(-sqrt_1_5) == a_cw[1]
    assert np.isnan(a_cw[2])
    assert approx(sqrt_1_5) == a_cw[3]


def test_scale_1d():
    trait_1d = np.array([0.0, 1.0, 2.0, 3.0])

    scaled_trait_1d = _pre_process_trait(trait_1d)

    sqrt_1_5 = np.sqrt(1.5)

    assert np.isnan(scaled_trait_1d[0])
    assert approx(-sqrt_1_5) == scaled_trait_1d[1]
    assert approx(0.0) == scaled_trait_1d[2]
    assert approx(sqrt_1_5) == scaled_trait_1d[3]


def test_scale_2d():
    trait_2d = np.array([[5.0, 1.0], [0.0, 3.0]])

    scaled_trait_2d = _pre_process_trait(trait_2d)

    sqrt_1_5 = np.sqrt(1.5)

    assert approx(sqrt_1_5) == scaled_trait_2d[0][0]
    assert approx(-sqrt_1_5) == scaled_trait_2d[0][1]
    assert np.isnan(scaled_trait_2d[1][0])
    assert approx(0.0) == scaled_trait_2d[1][1]


def test_process():
    a_lai = np.array([[0.87938678, 1.16446712, 1.22641223, 0.91329112, 1.51065969,
                       1.22097301, 0.85111759, 1.59934332, 1.12270911, 1.5701302],
                      [1.10951792, 1.30872184, 1.19120714, 1.32458738, 0.93088555,
                       1.49808699, 1.57594138, 1.44594414, 0.91541966, 1.46568688],
                      [0.88668766, 1.33503956, 1.45993834, 0.98021515, 0.86927832,
                       1.37552177, 0.86927602, 0.84557555, 0.87699175, 1.57778646],
                      [1.53492533, 1.52005562, 0.87759379, 1.29141713, 1.29742173,
                       1.41679098, 1.57653808, 1.26925031, 1.50252092, 0.82244487],
                      [1.53654894, 1.53208312, 1.48550786, 1.58223853, 1.15228171,
                       1.48642302, 1.51603717, 1.55718918, 0.87509568, 1.45378371],
                      [0.97760941, 1.2237723, 1.23745615, 1.52805101, 1.58248682,
                       0.8363865, 1.13917848, 1.57457709, 0.90368241, 1.56440414],
                      [1.14370198, 0.98871949, 0.83849553, 1.28032683, 0.89171812,
                       1.42943354, 1.53807144, 0.87983198, 0.82465269, 0.9512418],
                      [0.86825614, 0.92547698, 1.1118817, 1.26763699, 0.86674554,
                       0.95593675, 0.8508761, 1.59323323, 0.83288445, 0.99263613],
                      [1.48326121, 1.15251358, 1.50958625, 0.86958476, 1.16161352,
                       0.89559247, 1.51967839, 0.8163617, 1.50590506, 1.40443048],
                      [1.40416266, 0.91458109, 1.56877472, 0.8411787, 0.85582287,
                       1.58993945, 1.43804445, 0.85035615, 1.42556831, 0.88719372]])
    a_cw = np.array([[0.50583365, 0.36237748, 0.49032708, 0.10173301, 0.92792562,
                      0.94923578, 0.40834234, 0.38602451, 0.43298894, 0.00109016],
                     [0.93020825, 0.79476352, 0.36177725, 0.81055002, 0.2128568,
                      0.97154312, 0.21546082, 0.71900572, 0.72117734, 0.03635445],
                     [0.24553259, 0.41212087, 0.28888077, 0.49815259, 0.56391852,
                      0.23507629, 0.99193694, 0.90933921, 0.13763819, 0.39191802],
                     [0.97522586, 0.63265333, 0.60910541, 0.61618778, 0.61565575,
                      0.86244576, 0.22756964, 0.95050188, 0.23530484, 0.96252923],
                     [0.71415863, 0.95106815, 0.42450392, 0.63878779, 0.59704219,
                      0.78879161, 0.08453717, 0.09000347, 0.90412677, 0.35907961],
                     [0.6200917, 0.18683279, 0.15765154, 0.26007168, 0.96021244,
                      0.19420245, 0.27872852, 0.50023529, 0.62837065, 0.62335185],
                     [0.75616754, 0.98318038, 0.04922419, 0.41519254, 0.90551963,
                      0.05493066, 0.5359981, 0.56202856, 0.52101045, 0.07447384],
                     [0.40137711, 0.3974881, 0.69912321, 0.98979935, 0.72946066,
                      0.34658135, 0.34841877, 0.2256088, 0.51256302, 0.68354124],
                     [0.42196108, 0.24635111, 0.02894214, 0.10739165, 0.39564489,
                      0.39795154, 0.79642257, 0.5865653, 0.05525797, 0.26143202],
                     [0.17002306, 0.69433121, 0.47829224, 0.56357375, 0.63415934,
                      0.59728232, 0.47128022, 0.66802419, 0.70903515, 0.03642678]])
    a_cab = np.array([[0.02941798, 0.8640849, 0.33103182, 0.81502056, 0.21802795,
                       0.52221852, 0.93351023, 0.25749816, 0.36857807, 0.12229718],
                      [0.83180554, 0.27555442, 0.49088614, 0.35693636, 0.96902993,
                       0.61005762, 0.67133881, 0.84172272, 0.12455516, 0.8978595],
                      [0.48537038, 0.42603801, 0.55467215, 0.45784111, 0.53571247,
                       0.68527041, 0.70287854, 0.63841539, 0.55872211, 0.02078435],
                      [0.11249342, 0.01218412, 0.02806516, 0.17727885, 0.08494202,
                       0.74768757, 0.5032687, 0.44523994, 0.76053097, 0.47228294],
                      [0.96533917, 0.92116133, 0.50656305, 0.51449833, 0.88677528,
                       0.79942681, 0.46220967, 0.50136665, 0.0624617, 0.11754491],
                      [0.6660223, 0.86980625, 0.27779489, 0.80088845, 0.232831,
                       0.13696704, 0.43306557, 0.91163307, 0.06285888, 0.81072612],
                      [0.80168946, 0.20274405, 0.67145501, 0.13029482, 0.37146871,
                       0.507429, 0.88701391, 0.77776377, 0.53365525, 0.55858227],
                      [0.58564618, 0.97090466, 0.21743641, 0.99886593, 0.05189815,
                       0.05839001, 0.94562788, 0.66540929, 0.02514091, 0.83510228],
                      [0.56234932, 0.63044499, 0.19530644, 0.84202734, 0.56493981,
                       0.24473101, 0.72317209, 0.45049538, 0.79147526, 0.17959897],
                      [0.08305292, 0.10973638, 0.88852854, 0.42643293, 0.09990597,
                       0.15200276, 0.5775525, 0.73609367, 0.82047272, 0.57943779]])

    results_dict = _process(a_lai, a_cw, a_cab, ['cvh', 'mnnd', 'fe', 'fdiv'])

    assert 4 == len(results_dict)
    assert 'cvh' in results_dict
    assert (10, 10) == results_dict['cvh'].shape
    assert approx(0.5543484553465773) == results_dict['cvh'][0][0].min()
    assert approx(0.5543484553465773) == results_dict['cvh'][0][0].max()
    assert 'mnnd' in results_dict
    assert (10, 10) == results_dict['mnnd'].shape
    assert approx(0.391185794479155) == results_dict['mnnd'][0][0].min()
    assert approx(0.391185794479155) == results_dict['mnnd'][0][0].max()
    assert 'fe' in results_dict
    assert (10, 10) == results_dict['fe'].shape
    assert approx(0.8162409410523356) == results_dict['fe'][0][0].min()
    assert approx(0.8162409410523356) == results_dict['fe'][0][0].max()
    assert 'fdiv' in results_dict
    assert (10, 10) == results_dict['fdiv'].shape
    assert approx(0.4698261066849253) == results_dict['fdiv'][0][0].min()
    assert approx(0.4698261066849253) == results_dict['fdiv'][0][0].max()


def test_cvh_function_get_name():
    assert 'cvh' == CVHFunction.get_name()


def test_cvh_function_func():
    cvh_function = CVHFunction(3, 3, 1, 1)
    traits = np.array([[0.1, 0.2, 0.3, 0.4, 0.4, 0.3, 0.1, 0.1, 0.2],
                       [0.2, 0.3, 0.2, 0.1, 0.5, 0.3, 0.5, 0.7, 0.2],
                       [0.4, 0.2, 0.2, 0.4, 0.6, 0.6, 0.3, 0.3, 0.2]])
    assert approx(0.02) == cvh_function._func(traits.T)


def test_mnnd_function_get_name():
    assert 'mnnd' == MNNDFunction.get_name()


def test_mnnd_function_func():
    mnnd_function = MNNDFunction(3, 3, 1, 1)
    traits = np.array([[0.1, 0.2, 0.3, 0.4, 0.4, 0.3, 0.1, 0.1, 0.2],
                       [0.2, 0.3, 0.2, 0.1, 0.5, 0.3, 0.5, 0.7, 0.2],
                       [0.4, 0.2, 0.2, 0.4, 0.6, 0.6, 0.3, 0.3, 0.2]])
    assert approx(1.1353556579106137) == mnnd_function._func(traits.T)


def test_fe_function_get_name():
    assert 'fe' == FEFunction.get_name()


def test_fe_function_func():
    fe_function = FEFunction(3, 3, 1, 1)
    traits = np.array([[0.1, 0.2, 0.3, 0.4, 0.4, 0.3, 0.1, 0.1, 0.2],
                       [0.2, 0.3, 0.2, 0.1, 0.5, 0.3, 0.5, 0.7, 0.2],
                       [0.4, 0.2, 0.2, 0.4, 0.6, 0.6, 0.3, 0.3, 0.2]])
    assert approx(0.8506660240031859) == fe_function._func(traits.T)


def test_fdiv_function_get_name():
    assert 'fdiv' == FDIVFunction.get_name()


def test_fdiv_function_func():
    fdiv_function = FDIVFunction(3, 3, 1, 1)
    traits = np.array([[0.1, 0.2, 0.3, 0.4, 0.4, 0.3, 0.1, 0.1, 0.2],
                       [0.2, 0.3, 0.2, 0.1, 0.5, 0.3, 0.5, 0.7, 0.2],
                       [0.4, 0.2, 0.2, 0.4, 0.6, 0.6, 0.3, 0.3, 0.2]])
    assert approx(0.252741939118282) == fdiv_function._func(traits.T)
