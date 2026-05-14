START TRANSACTION;

SET FOREIGN_KEY_CHECKS = 0;
TRUNCATE TABLE `SERVICE_PRICES`;
TRUNCATE TABLE `SERVICES`;
SET FOREIGN_KEY_CHECKS = 1;

INSERT INTO `SERVICES` (`hospital_id`,`code`,`name`,`description`,`aliases`,`status`)
VALUES
(1, 'DG05', 'Khám chức năng hô hấp', NULL, NULL, 1),
(1, 'DG06', 'Khám da liễu', NULL, NULL, 1),
(1, 'ND98', 'Khám hậu môn-trực tràng', NULL, NULL, 1),
(1, 'DG10', 'Khám mắt', NULL, NULL, 1),
(1, 'DG12', 'Khám Tiết niệu', NULL, NULL, 1),
(1, 'DG13', 'Khám nội tiết', NULL, NULL, 1),
(1, 'DG14', 'Khám phổi', NULL, NULL, 1),
(1, 'DG15', 'Khám phụ khoa', NULL, NULL, 1),
(1, 'DG19', 'Khám tai mũi họng', NULL, NULL, 1),
(1, 'DG20', 'Khám thần kinh', NULL, NULL, 1),
(1, 'DG21', 'Khám tiêu hoá - gan mật', NULL, NULL, 1),
(1, 'DG22', 'Khám tim mạch', NULL, NULL, 1),
(1, 'DG25', 'Khám viêm gan', NULL, NULL, 1),
(1, 'DG26', 'Khám xương khớp', NULL, NULL, 1),
(1, 'DG29', 'Khám lồng ngực', NULL, NULL, 1),
(1, 'DG46', 'Khám Nhi', NULL, NULL, 1),
(1, 'DG62', 'Khám nội thận', NULL, NULL, 1),
(1, 'DG63', 'Khám thai', NULL, NULL, 1),
(1, 'EAAR01', 'Phòng 2 giường- Giường Nội khoa loại 2 Hạng I', NULL, NULL, 1),
(1, 'EAAR02', 'Phòng 2 giường- Giường Ngoại khoa loại 4 Hạng I', NULL, NULL, 1),
(1, 'EAAR03', 'Phòng 2 giường- Giường Ngoại khoa loại 3 Hạng I', NULL, NULL, 1),
(1, 'EAAR04', 'Phòng 2 giường- Giường Ngoại khoa loại 2 Hạng I', NULL, NULL, 1),
(1, 'EAAR05', 'Phòng 2 giường- Giường Ngoại khoa loại 1 Hạng I', NULL, NULL, 1),
(1, 'EAAS', 'Phòng 4 giường- Giường Nội khoa loại 2 Hạng I', NULL, NULL, 1),
(1, 'MC72', 'Siêu âm Doppler tinh hoàn, mào tinh hoàn hai bên', NULL, NULL, 1),
(1, 'MC73', 'Siêu âm ổ bụng', NULL, NULL, 1),
(1, 'MC76', 'Siêu âm cơ phần mềm vùng cổ', NULL, NULL, 1),
(1, 'MC82', 'Siêu âm Doppler mạch máu ổ bụng (động mạch chủ, mạc treo tràng trên, thân tạng…)', NULL, NULL, 1),
(1, 'MC89', 'Siêu âm phần mềm', NULL, NULL, 1),
(1, 'MC95', 'Siêu âm Doppler tử cung, buồng trứng qua đường âm đạo', NULL, NULL, 1),
(1, 'MCA5', 'Siêu âm tuyến giáp', NULL, NULL, 1),
(1, 'MD18', 'Siêu âm Doppler tim thai (sàng lọc)', NULL, NULL, 1),
(1, 'MD19', 'Siêu âm Doppler tim thai (song thai trở lên) (sàng lọc)', NULL, NULL, 1),
(1, 'MD08', 'Siêu âm Doppler tim', NULL, NULL, 1),
(1, 'ND91', 'Chụp CLVT hàm-mặt có tiêm thuốc cản quang (sọ + xoang) (chưa bao gồm thuốc cản quang) [BHYT thanh toán theo đơn giá 1-32 dãy]', NULL, NULL, 1),
(1, 'ND92', 'Chụp CLVT sọ não không tiêm thuốc cản quang [BHYT thanh toán theo đơn giá 1-32 dãy]', NULL, NULL, 1),
(1, 'ND93', 'Chụp CLVT sọ não có tiêm thuốc cản quang (chưa bao gồm thuốc cản quang) [BHYT thanh toán theo đơn giá 1-32 dãy]', NULL, NULL, 1),
(1, 'ND94', 'Chụp CT-Scan vùng cổ [BHYT thanh toán theo đơn giá 1-32 dãy]', NULL, NULL, 1),
(1, 'ND95', 'Chụp CT-Scan vùng cổ có thuốc cản quang (chưa bao gồm thuốc cản quang) [BHYT thanh toán theo đơn giá 1-32 dãy]', NULL, NULL, 1),
(1, 'ND96', 'Chụp CLVT hàm-mặt không tiêm thuốc cản quang (xoang) [BHYT thanh toán theo đơn giá 1-32 dãy]', NULL, NULL, 1),
(1, 'ND97', 'Chụp CLVT hàm-mặt có tiêm thuốc cản quang (chưa bao gồm thuốc cản quang) [BHYT thanh toán theo đơn giá 1-32 dãy]', NULL, NULL, 1),
(1, 'MAA4', 'Chụp X-quang bàn chân nghiêng số hóa 1 phim', NULL, NULL, 1),
(1, 'MAA5', 'Chụp X-quang bàn chân thẳng số hóa 1 phim', NULL, NULL, 1),
(1, 'MAA6', 'Chụp X-quang bàn chân thẳng-nghiêng số hóa 1 phim', NULL, NULL, 1),
(1, 'MAB0', 'Chụp X-quang bản lề chẩm-cổ (C1-C2) T-N số hóa 1 phim', NULL, NULL, 1),
(1, 'MAC7', 'Chụp X-quang Cẳng chân thẳng và nghiêng số hóa 1 phim', NULL, NULL, 1),
(1, 'MAD1', 'Chụp X-quang Cổ chân thẳng-nghiêng số hóa 1 phim', NULL, NULL, 1),
(1, 'MAD5', 'Chụp X-quang Cổ tay thẳng-nghiêng số hóa 1 phim', NULL, NULL, 1),
(1, 'MH45', 'Đo hoạt độ LDH ( Lactat dehydrogenase)', NULL, NULL, 1),
(1, 'MH46', 'Định lượng Amoniac ( NH3)', NULL, NULL, 1),
(1, 'MH47', 'Định lượng Calci ion hóa', NULL, NULL, 1),
(1, 'MH51', 'Đo hoạt độ CK-MB (Isozym MB of Creatine kinase)', NULL, NULL, 1),
(1, 'MH52', 'Định lượng IgG', NULL, NULL, 1),
(1, 'MH26', 'Định lượng Glucose sau ăn 2 giờ', NULL, NULL, 1),
(1, 'MH27', 'Streptococcus pyogenes ASO', NULL, NULL, 1),
(1, 'MI29', 'Xét nghiệm hồng cầu lưới (bằng máy đếm laser)', NULL, NULL, 1),
(1, 'MI35', 'Vi nấm nhuộm soi DNT', NULL, NULL, 1),
(1, 'MI42', 'Huyết đồ (bằng máy đếm laser)', NULL, NULL, 1),
(1, 'MI45', 'Định lượng D-Dimer', NULL, NULL, 1),
(1, 'MI48', 'Xét nghiệm hòa hợp trong phát máu (Định nhóm máu hệ ABO, Rh (D), AHG bằng phương pháp Gelcard (Crossmatch))', NULL, NULL, 1),
(1, 'MJ57', 'Định lượng LH (Luteinizing Hormone)', NULL, NULL, 1),
(1, 'MJ63', 'Định lượng CA 19 - 9 (Carbohydrate Antigen 19-9)', NULL, NULL, 1),
(1, 'MJ64', 'HBc IgM miễn dịch tự động', NULL, NULL, 1),
(1, 'MJ65', 'HAV IgM miễn dịch tự động', NULL, NULL, 1),
(1, 'MJ66', 'HAV total miễn dịch tự động', NULL, NULL, 1),
(1, 'MB82', 'Nội soi can thiệp - cắt polyp ống tiêu hóa > 1cm hoặc nhiều polyp', NULL, NULL, 1),
(1, 'MBB3', 'Nội soi thực quản - dạ dày - tá tràng có sinh thiết (ống mềm)', NULL, NULL, 1),
(1, 'MBB4', 'Nội soi trực tràng ống mềm không sinh thiết (có thuốc)', NULL, NULL, 1),
(1, 'MBB5', 'Nội soi trực tràng ống mềm không sinh thiết (không thuốc)', NULL, NULL, 1),
(1, 'MBH6', 'Nội soi đại tràng cắt polyp ≤ 1 cm gây mê (có soi chẩn đoán)', NULL, NULL, 1),
(1, 'TZ01', 'Nội soi tai mũi họng', NULL, NULL, 1),
(1, 'TZ02', 'Nội soi tai', NULL, NULL, 1),
(1, 'TZ03', 'Nội soi mũi xoang', NULL, NULL, 1),
(1, 'TZ04', 'Nội soi họng', NULL, NULL, 1),
(1, 'N108', 'Phẫu thuật tạo hình điều trị tật thừa ngón tay', NULL, NULL, 1),
(1, 'N120', 'Phẫu thuật điều trị bệnh DE QUER VAIN và ngón tay cò súng [gây mê]', NULL, NULL, 1),
(1, 'N125', 'Khâu da thì 2 (phòng mổ)', NULL, NULL, 1),
(1, 'N128', 'Nắn, bó bột gãy xương chậu', NULL, NULL, 1),
(1, 'L097', 'Phẫu thuật mở bụng bóc u xơ tử cung', NULL, NULL, 1),
(1, 'L101', 'Cắt cụt cổ tử cung [gây mê]', NULL, NULL, 1),
(1, 'L104', 'Phẫu thuật nội soi cắt phần phụ', NULL, NULL, 1),
(1, 'L106', 'Thủ thuật xoắn polip cổ tử cung, âm đạo', NULL, NULL, 1),
(1, 'H183', 'Lấy sỏi niệu quản qua nội soi (qua ngã niệu đạo)', NULL, NULL, 1),
(1, 'H189', 'Nội soi bàng quang, bơm rửa lấy máu cục tránh phẫu thuật', NULL, NULL, 1),
(1, 'H190', 'Nội soi niệu quản chẩn đoán', NULL, NULL, 1),
(1, 'R105', 'Chích áp xe lợi', NULL, NULL, 1),
(1, 'R106', 'Chích tháo mủ trong áp xe nông vùng hàm mặt', NULL, NULL, 1),
(1, 'R113', 'Cố định tạm thời sơ cứu gãy xương hàm', NULL, NULL, 1),
(1, 'MF20', 'Điện tim thường (ECG)', NULL, NULL, 1),
(1, 'MF22', 'Đo áp lực hậu môn trực tràng', NULL, NULL, 1),
(1, 'MF23', 'Đo chức năng hô hấp có thuốc', NULL, NULL, 1),
(1, 'NZN1', 'Vi khuẩn nuôi cấy và định danh hệ thống tự động (dịch khớp)', NULL, NULL, 1),
(1, 'NZP2', 'Mycobacterium tuberculosis định danh và kháng RMP Xpert', NULL, NULL, 1),
(1, 'NZp3', 'Vi nấm soi tươi', NULL, NULL, 1),
(1, 'MQ15', 'HBV genotype Real-time PCR', NULL, NULL, 1),
(1, 'MQ16', 'Mycobacterium tuberculosis Real-time PCR /đàm', NULL, NULL, 1),
(1, 'TPO5', 'Nhuộm hóa mô miễn dịch cho mỗi một dấu ấn (kháng thể SYNAPTOPHYSIN)', NULL, NULL, 1),
(1, 'TPP1', 'Nhuộm hóa mô miễn dịch cho một dấu ấn (kháng thể PD-L1 (SP263))', NULL, NULL, 1),
(1, 'I121', 'Chọc hút khí màng phổi', NULL, NULL, 1),
(1, 'I122', 'Bơm rửa khoang màng phổi', NULL, NULL, 1);

INSERT INTO `SERVICE_PRICES` (`service_id`,`hospital_id`,`price`,`currency`,`payer_type`,`area_tag`,`effective_from`,`effective_to`,`notes`,`status`)
SELECT `service_id`, 1, 150000.00, 'VND', 'TU_CHI_TRA', NULL, '2024-01-01', NULL, NULL, 1
FROM `SERVICES`
WHERE `hospital_id` = 1 AND `code` = 'DG05';

INSERT INTO `SERVICE_PRICES` (`service_id`,`hospital_id`,`price`,`currency`,`payer_type`,`area_tag`,`effective_from`,`effective_to`,`notes`,`status`)
SELECT `service_id`, 1, 50600.00, 'VND', 'BHYT', NULL, '2024-01-01', NULL, NULL, 1
FROM `SERVICES`
WHERE `hospital_id` = 1 AND `code` = 'DG05';

INSERT INTO `SERVICE_PRICES` (`service_id`,`hospital_id`,`price`,`currency`,`payer_type`,`area_tag`,`effective_from`,`effective_to`,`notes`,`status`)
SELECT `service_id`, 1, 150000.00, 'VND', 'TU_CHI_TRA', NULL, '2024-01-01', NULL, NULL, 1
FROM `SERVICES`
WHERE `hospital_id` = 1 AND `code` = 'DG06';

INSERT INTO `SERVICE_PRICES` (`service_id`,`hospital_id`,`price`,`currency`,`payer_type`,`area_tag`,`effective_from`,`effective_to`,`notes`,`status`)
SELECT `service_id`, 1, 50600.00, 'VND', 'BHYT', NULL, '2024-01-01', NULL, NULL, 1
FROM `SERVICES`
WHERE `hospital_id` = 1 AND `code` = 'DG06';

INSERT INTO `SERVICE_PRICES` (`service_id`,`hospital_id`,`price`,`currency`,`payer_type`,`area_tag`,`effective_from`,`effective_to`,`notes`,`status`)
SELECT `service_id`, 1, 150000.00, 'VND', 'TU_CHI_TRA', NULL, '2024-01-01', NULL, NULL, 1
FROM `SERVICES`
WHERE `hospital_id` = 1 AND `code` = 'ND98';

INSERT INTO `SERVICE_PRICES` (`service_id`,`hospital_id`,`price`,`currency`,`payer_type`,`area_tag`,`effective_from`,`effective_to`,`notes`,`status`)
SELECT `service_id`, 1, 50600.00, 'VND', 'BHYT', NULL, '2024-01-01', NULL, NULL, 1
FROM `SERVICES`
WHERE `hospital_id` = 1 AND `code` = 'ND98';

INSERT INTO `SERVICE_PRICES` (`service_id`,`hospital_id`,`price`,`currency`,`payer_type`,`area_tag`,`effective_from`,`effective_to`,`notes`,`status`)
SELECT `service_id`, 1, 150000.00, 'VND', 'TU_CHI_TRA', NULL, '2024-01-01', NULL, NULL, 1
FROM `SERVICES`
WHERE `hospital_id` = 1 AND `code` = 'DG10';

INSERT INTO `SERVICE_PRICES` (`service_id`,`hospital_id`,`price`,`currency`,`payer_type`,`area_tag`,`effective_from`,`effective_to`,`notes`,`status`)
SELECT `service_id`, 1, 50600.00, 'VND', 'BHYT', NULL, '2024-01-01', NULL, NULL, 1
FROM `SERVICES`
WHERE `hospital_id` = 1 AND `code` = 'DG10';

INSERT INTO `SERVICE_PRICES` (`service_id`,`hospital_id`,`price`,`currency`,`payer_type`,`area_tag`,`effective_from`,`effective_to`,`notes`,`status`)
SELECT `service_id`, 1, 150000.00, 'VND', 'TU_CHI_TRA', NULL, '2024-01-01', NULL, NULL, 1
FROM `SERVICES`
WHERE `hospital_id` = 1 AND `code` = 'DG12';

INSERT INTO `SERVICE_PRICES` (`service_id`,`hospital_id`,`price`,`currency`,`payer_type`,`area_tag`,`effective_from`,`effective_to`,`notes`,`status`)
SELECT `service_id`, 1, 50600.00, 'VND', 'BHYT', NULL, '2024-01-01', NULL, NULL, 1
FROM `SERVICES`
WHERE `hospital_id` = 1 AND `code` = 'DG12';

INSERT INTO `SERVICE_PRICES` (`service_id`,`hospital_id`,`price`,`currency`,`payer_type`,`area_tag`,`effective_from`,`effective_to`,`notes`,`status`)
SELECT `service_id`, 1, 150000.00, 'VND', 'TU_CHI_TRA', NULL, '2024-01-01', NULL, NULL, 1
FROM `SERVICES`
WHERE `hospital_id` = 1 AND `code` = 'DG13';

INSERT INTO `SERVICE_PRICES` (`service_id`,`hospital_id`,`price`,`currency`,`payer_type`,`area_tag`,`effective_from`,`effective_to`,`notes`,`status`)
SELECT `service_id`, 1, 50600.00, 'VND', 'BHYT', NULL, '2024-01-01', NULL, NULL, 1
FROM `SERVICES`
WHERE `hospital_id` = 1 AND `code` = 'DG13';

INSERT INTO `SERVICE_PRICES` (`service_id`,`hospital_id`,`price`,`currency`,`payer_type`,`area_tag`,`effective_from`,`effective_to`,`notes`,`status`)
SELECT `service_id`, 1, 150000.00, 'VND', 'TU_CHI_TRA', NULL, '2024-01-01', NULL, NULL, 1
FROM `SERVICES`
WHERE `hospital_id` = 1 AND `code` = 'DG14';

INSERT INTO `SERVICE_PRICES` (`service_id`,`hospital_id`,`price`,`currency`,`payer_type`,`area_tag`,`effective_from`,`effective_to`,`notes`,`status`)
SELECT `service_id`, 1, 50600.00, 'VND', 'BHYT', NULL, '2024-01-01', NULL, NULL, 1
FROM `SERVICES`
WHERE `hospital_id` = 1 AND `code` = 'DG14';

INSERT INTO `SERVICE_PRICES` (`service_id`,`hospital_id`,`price`,`currency`,`payer_type`,`area_tag`,`effective_from`,`effective_to`,`notes`,`status`)
SELECT `service_id`, 1, 150000.00, 'VND', 'TU_CHI_TRA', NULL, '2024-01-01', NULL, NULL, 1
FROM `SERVICES`
WHERE `hospital_id` = 1 AND `code` = 'DG15';

INSERT INTO `SERVICE_PRICES` (`service_id`,`hospital_id`,`price`,`currency`,`payer_type`,`area_tag`,`effective_from`,`effective_to`,`notes`,`status`)
SELECT `service_id`, 1, 50600.00, 'VND', 'BHYT', NULL, '2024-01-01', NULL, NULL, 1
FROM `SERVICES`
WHERE `hospital_id` = 1 AND `code` = 'DG15';

INSERT INTO `SERVICE_PRICES` (`service_id`,`hospital_id`,`price`,`currency`,`payer_type`,`area_tag`,`effective_from`,`effective_to`,`notes`,`status`)
SELECT `service_id`, 1, 150000.00, 'VND', 'TU_CHI_TRA', NULL, '2024-01-01', NULL, NULL, 1
FROM `SERVICES`
WHERE `hospital_id` = 1 AND `code` = 'DG19';

INSERT INTO `SERVICE_PRICES` (`service_id`,`hospital_id`,`price`,`currency`,`payer_type`,`area_tag`,`effective_from`,`effective_to`,`notes`,`status`)
SELECT `service_id`, 1, 50600.00, 'VND', 'BHYT', NULL, '2024-01-01', NULL, NULL, 1
FROM `SERVICES`
WHERE `hospital_id` = 1 AND `code` = 'DG19';

INSERT INTO `SERVICE_PRICES` (`service_id`,`hospital_id`,`price`,`currency`,`payer_type`,`area_tag`,`effective_from`,`effective_to`,`notes`,`status`)
SELECT `service_id`, 1, 150000.00, 'VND', 'TU_CHI_TRA', NULL, '2024-01-01', NULL, NULL, 1
FROM `SERVICES`
WHERE `hospital_id` = 1 AND `code` = 'DG20';

INSERT INTO `SERVICE_PRICES` (`service_id`,`hospital_id`,`price`,`currency`,`payer_type`,`area_tag`,`effective_from`,`effective_to`,`notes`,`status`)
SELECT `service_id`, 1, 50600.00, 'VND', 'BHYT', NULL, '2024-01-01', NULL, NULL, 1
FROM `SERVICES`
WHERE `hospital_id` = 1 AND `code` = 'DG20';

INSERT INTO `SERVICE_PRICES` (`service_id`,`hospital_id`,`price`,`currency`,`payer_type`,`area_tag`,`effective_from`,`effective_to`,`notes`,`status`)
SELECT `service_id`, 1, 150000.00, 'VND', 'TU_CHI_TRA', NULL, '2024-01-01', NULL, NULL, 1
FROM `SERVICES`
WHERE `hospital_id` = 1 AND `code` = 'DG21';

INSERT INTO `SERVICE_PRICES` (`service_id`,`hospital_id`,`price`,`currency`,`payer_type`,`area_tag`,`effective_from`,`effective_to`,`notes`,`status`)
SELECT `service_id`, 1, 50600.00, 'VND', 'BHYT', NULL, '2024-01-01', NULL, NULL, 1
FROM `SERVICES`
WHERE `hospital_id` = 1 AND `code` = 'DG21';

INSERT INTO `SERVICE_PRICES` (`service_id`,`hospital_id`,`price`,`currency`,`payer_type`,`area_tag`,`effective_from`,`effective_to`,`notes`,`status`)
SELECT `service_id`, 1, 150000.00, 'VND', 'TU_CHI_TRA', NULL, '2024-01-01', NULL, NULL, 1
FROM `SERVICES`
WHERE `hospital_id` = 1 AND `code` = 'DG22';

INSERT INTO `SERVICE_PRICES` (`service_id`,`hospital_id`,`price`,`currency`,`payer_type`,`area_tag`,`effective_from`,`effective_to`,`notes`,`status`)
SELECT `service_id`, 1, 50600.00, 'VND', 'BHYT', NULL, '2024-01-01', NULL, NULL, 1
FROM `SERVICES`
WHERE `hospital_id` = 1 AND `code` = 'DG22';

INSERT INTO `SERVICE_PRICES` (`service_id`,`hospital_id`,`price`,`currency`,`payer_type`,`area_tag`,`effective_from`,`effective_to`,`notes`,`status`)
SELECT `service_id`, 1, 150000.00, 'VND', 'TU_CHI_TRA', NULL, '2024-01-01', NULL, NULL, 1
FROM `SERVICES`
WHERE `hospital_id` = 1 AND `code` = 'DG25';

INSERT INTO `SERVICE_PRICES` (`service_id`,`hospital_id`,`price`,`currency`,`payer_type`,`area_tag`,`effective_from`,`effective_to`,`notes`,`status`)
SELECT `service_id`, 1, 50600.00, 'VND', 'BHYT', NULL, '2024-01-01', NULL, NULL, 1
FROM `SERVICES`
WHERE `hospital_id` = 1 AND `code` = 'DG25';

INSERT INTO `SERVICE_PRICES` (`service_id`,`hospital_id`,`price`,`currency`,`payer_type`,`area_tag`,`effective_from`,`effective_to`,`notes`,`status`)
SELECT `service_id`, 1, 150000.00, 'VND', 'TU_CHI_TRA', NULL, '2024-01-01', NULL, NULL, 1
FROM `SERVICES`
WHERE `hospital_id` = 1 AND `code` = 'DG26';

INSERT INTO `SERVICE_PRICES` (`service_id`,`hospital_id`,`price`,`currency`,`payer_type`,`area_tag`,`effective_from`,`effective_to`,`notes`,`status`)
SELECT `service_id`, 1, 50600.00, 'VND', 'BHYT', NULL, '2024-01-01', NULL, NULL, 1
FROM `SERVICES`
WHERE `hospital_id` = 1 AND `code` = 'DG26';

INSERT INTO `SERVICE_PRICES` (`service_id`,`hospital_id`,`price`,`currency`,`payer_type`,`area_tag`,`effective_from`,`effective_to`,`notes`,`status`)
SELECT `service_id`, 1, 150000.00, 'VND', 'TU_CHI_TRA', NULL, '2024-01-01', NULL, NULL, 1
FROM `SERVICES`
WHERE `hospital_id` = 1 AND `code` = 'DG29';

INSERT INTO `SERVICE_PRICES` (`service_id`,`hospital_id`,`price`,`currency`,`payer_type`,`area_tag`,`effective_from`,`effective_to`,`notes`,`status`)
SELECT `service_id`, 1, 50600.00, 'VND', 'BHYT', NULL, '2024-01-01', NULL, NULL, 1
FROM `SERVICES`
WHERE `hospital_id` = 1 AND `code` = 'DG29';

INSERT INTO `SERVICE_PRICES` (`service_id`,`hospital_id`,`price`,`currency`,`payer_type`,`area_tag`,`effective_from`,`effective_to`,`notes`,`status`)
SELECT `service_id`, 1, 150000.00, 'VND', 'TU_CHI_TRA', NULL, '2024-01-01', NULL, NULL, 1
FROM `SERVICES`
WHERE `hospital_id` = 1 AND `code` = 'DG46';

INSERT INTO `SERVICE_PRICES` (`service_id`,`hospital_id`,`price`,`currency`,`payer_type`,`area_tag`,`effective_from`,`effective_to`,`notes`,`status`)
SELECT `service_id`, 1, 50600.00, 'VND', 'BHYT', NULL, '2024-01-01', NULL, NULL, 1
FROM `SERVICES`
WHERE `hospital_id` = 1 AND `code` = 'DG46';

INSERT INTO `SERVICE_PRICES` (`service_id`,`hospital_id`,`price`,`currency`,`payer_type`,`area_tag`,`effective_from`,`effective_to`,`notes`,`status`)
SELECT `service_id`, 1, 150000.00, 'VND', 'TU_CHI_TRA', NULL, '2024-01-01', NULL, NULL, 1
FROM `SERVICES`
WHERE `hospital_id` = 1 AND `code` = 'DG62';

INSERT INTO `SERVICE_PRICES` (`service_id`,`hospital_id`,`price`,`currency`,`payer_type`,`area_tag`,`effective_from`,`effective_to`,`notes`,`status`)
SELECT `service_id`, 1, 50600.00, 'VND', 'BHYT', NULL, '2024-01-01', NULL, NULL, 1
FROM `SERVICES`
WHERE `hospital_id` = 1 AND `code` = 'DG62';

INSERT INTO `SERVICE_PRICES` (`service_id`,`hospital_id`,`price`,`currency`,`payer_type`,`area_tag`,`effective_from`,`effective_to`,`notes`,`status`)
SELECT `service_id`, 1, 150000.00, 'VND', 'TU_CHI_TRA', NULL, '2024-01-01', NULL, NULL, 1
FROM `SERVICES`
WHERE `hospital_id` = 1 AND `code` = 'DG63';

INSERT INTO `SERVICE_PRICES` (`service_id`,`hospital_id`,`price`,`currency`,`payer_type`,`area_tag`,`effective_from`,`effective_to`,`notes`,`status`)
SELECT `service_id`, 1, 50600.00, 'VND', 'BHYT', NULL, '2024-01-01', NULL, NULL, 1
FROM `SERVICES`
WHERE `hospital_id` = 1 AND `code` = 'DG63';

INSERT INTO `SERVICE_PRICES` (`service_id`,`hospital_id`,`price`,`currency`,`payer_type`,`area_tag`,`effective_from`,`effective_to`,`notes`,`status`)
SELECT `service_id`, 1, 1900000.00, 'VND', 'TU_CHI_TRA', NULL, '2024-01-01', NULL, NULL, 1
FROM `SERVICES`
WHERE `hospital_id` = 1 AND `code` = 'EAAR01';

INSERT INTO `SERVICE_PRICES` (`service_id`,`hospital_id`,`price`,`currency`,`payer_type`,`area_tag`,`effective_from`,`effective_to`,`notes`,`status`)
SELECT `service_id`, 1, 273800.00, 'VND', 'BHYT', NULL, '2024-01-01', NULL, NULL, 1
FROM `SERVICES`
WHERE `hospital_id` = 1 AND `code` = 'EAAR01';

INSERT INTO `SERVICE_PRICES` (`service_id`,`hospital_id`,`price`,`currency`,`payer_type`,`area_tag`,`effective_from`,`effective_to`,`notes`,`status`)
SELECT `service_id`, 1, 1900000.00, 'VND', 'TU_CHI_TRA', NULL, '2024-01-01', NULL, NULL, 1
FROM `SERVICES`
WHERE `hospital_id` = 1 AND `code` = 'EAAR02';

INSERT INTO `SERVICE_PRICES` (`service_id`,`hospital_id`,`price`,`currency`,`payer_type`,`area_tag`,`effective_from`,`effective_to`,`notes`,`status`)
SELECT `service_id`, 1, 286700.00, 'VND', 'BHYT', NULL, '2024-01-01', NULL, NULL, 1
FROM `SERVICES`
WHERE `hospital_id` = 1 AND `code` = 'EAAR02';

INSERT INTO `SERVICE_PRICES` (`service_id`,`hospital_id`,`price`,`currency`,`payer_type`,`area_tag`,`effective_from`,`effective_to`,`notes`,`status`)
SELECT `service_id`, 1, 1900000.00, 'VND', 'TU_CHI_TRA', NULL, '2024-01-01', NULL, NULL, 1
FROM `SERVICES`
WHERE `hospital_id` = 1 AND `code` = 'EAAR03';

INSERT INTO `SERVICE_PRICES` (`service_id`,`hospital_id`,`price`,`currency`,`payer_type`,`area_tag`,`effective_from`,`effective_to`,`notes`,`status`)
SELECT `service_id`, 1, 320700.00, 'VND', 'BHYT', NULL, '2024-01-01', NULL, NULL, 1
FROM `SERVICES`
WHERE `hospital_id` = 1 AND `code` = 'EAAR03';

INSERT INTO `SERVICE_PRICES` (`service_id`,`hospital_id`,`price`,`currency`,`payer_type`,`area_tag`,`effective_from`,`effective_to`,`notes`,`status`)
SELECT `service_id`, 1, 1900000.00, 'VND', 'TU_CHI_TRA', NULL, '2024-01-01', NULL, NULL, 1
FROM `SERVICES`
WHERE `hospital_id` = 1 AND `code` = 'EAAR04';

INSERT INTO `SERVICE_PRICES` (`service_id`,`hospital_id`,`price`,`currency`,`payer_type`,`area_tag`,`effective_from`,`effective_to`,`notes`,`status`)
SELECT `service_id`, 1, 364400.00, 'VND', 'BHYT', NULL, '2024-01-01', NULL, NULL, 1
FROM `SERVICES`
WHERE `hospital_id` = 1 AND `code` = 'EAAR04';

INSERT INTO `SERVICE_PRICES` (`service_id`,`hospital_id`,`price`,`currency`,`payer_type`,`area_tag`,`effective_from`,`effective_to`,`notes`,`status`)
SELECT `service_id`, 1, 1900000.00, 'VND', 'TU_CHI_TRA', NULL, '2024-01-01', NULL, NULL, 1
FROM `SERVICES`
WHERE `hospital_id` = 1 AND `code` = 'EAAR05';

INSERT INTO `SERVICE_PRICES` (`service_id`,`hospital_id`,`price`,`currency`,`payer_type`,`area_tag`,`effective_from`,`effective_to`,`notes`,`status`)
SELECT `service_id`, 1, 400400.00, 'VND', 'BHYT', NULL, '2024-01-01', NULL, NULL, 1
FROM `SERVICES`
WHERE `hospital_id` = 1 AND `code` = 'EAAR05';

INSERT INTO `SERVICE_PRICES` (`service_id`,`hospital_id`,`price`,`currency`,`payer_type`,`area_tag`,`effective_from`,`effective_to`,`notes`,`status`)
SELECT `service_id`, 1, 1500000.00, 'VND', 'TU_CHI_TRA', NULL, '2024-01-01', NULL, NULL, 1
FROM `SERVICES`
WHERE `hospital_id` = 1 AND `code` = 'EAAS';

INSERT INTO `SERVICE_PRICES` (`service_id`,`hospital_id`,`price`,`currency`,`payer_type`,`area_tag`,`effective_from`,`effective_to`,`notes`,`status`)
SELECT `service_id`, 1, 273800.00, 'VND', 'BHYT', NULL, '2024-01-01', NULL, NULL, 1
FROM `SERVICES`
WHERE `hospital_id` = 1 AND `code` = 'EAAS';

INSERT INTO `SERVICE_PRICES` (`service_id`,`hospital_id`,`price`,`currency`,`payer_type`,`area_tag`,`effective_from`,`effective_to`,`notes`,`status`)
SELECT `service_id`, 1, 400000.00, 'VND', 'TU_CHI_TRA', NULL, '2024-01-01', NULL, NULL, 1
FROM `SERVICES`
WHERE `hospital_id` = 1 AND `code` = 'MC72';

INSERT INTO `SERVICE_PRICES` (`service_id`,`hospital_id`,`price`,`currency`,`payer_type`,`area_tag`,`effective_from`,`effective_to`,`notes`,`status`)
SELECT `service_id`, 1, 89300.00, 'VND', 'BHYT', NULL, '2024-01-01', NULL, NULL, 1
FROM `SERVICES`
WHERE `hospital_id` = 1 AND `code` = 'MC72';

INSERT INTO `SERVICE_PRICES` (`service_id`,`hospital_id`,`price`,`currency`,`payer_type`,`area_tag`,`effective_from`,`effective_to`,`notes`,`status`)
SELECT `service_id`, 1, 150000.00, 'VND', 'TU_CHI_TRA', NULL, '2024-01-01', NULL, NULL, 1
FROM `SERVICES`
WHERE `hospital_id` = 1 AND `code` = 'MC73';

INSERT INTO `SERVICE_PRICES` (`service_id`,`hospital_id`,`price`,`currency`,`payer_type`,`area_tag`,`effective_from`,`effective_to`,`notes`,`status`)
SELECT `service_id`, 1, 58600.00, 'VND', 'BHYT', NULL, '2024-01-01', NULL, NULL, 1
FROM `SERVICES`
WHERE `hospital_id` = 1 AND `code` = 'MC73';

INSERT INTO `SERVICE_PRICES` (`service_id`,`hospital_id`,`price`,`currency`,`payer_type`,`area_tag`,`effective_from`,`effective_to`,`notes`,`status`)
SELECT `service_id`, 1, 150000.00, 'VND', 'TU_CHI_TRA', NULL, '2024-01-01', NULL, NULL, 1
FROM `SERVICES`
WHERE `hospital_id` = 1 AND `code` = 'MC76';

INSERT INTO `SERVICE_PRICES` (`service_id`,`hospital_id`,`price`,`currency`,`payer_type`,`area_tag`,`effective_from`,`effective_to`,`notes`,`status`)
SELECT `service_id`, 1, 58600.00, 'VND', 'BHYT', NULL, '2024-01-01', NULL, NULL, 1
FROM `SERVICES`
WHERE `hospital_id` = 1 AND `code` = 'MC76';

INSERT INTO `SERVICE_PRICES` (`service_id`,`hospital_id`,`price`,`currency`,`payer_type`,`area_tag`,`effective_from`,`effective_to`,`notes`,`status`)
SELECT `service_id`, 1, 400000.00, 'VND', 'TU_CHI_TRA', NULL, '2024-01-01', NULL, NULL, 1
FROM `SERVICES`
WHERE `hospital_id` = 1 AND `code` = 'MC82';

INSERT INTO `SERVICE_PRICES` (`service_id`,`hospital_id`,`price`,`currency`,`payer_type`,`area_tag`,`effective_from`,`effective_to`,`notes`,`status`)
SELECT `service_id`, 1, 252300.00, 'VND', 'BHYT', NULL, '2024-01-01', NULL, NULL, 1
FROM `SERVICES`
WHERE `hospital_id` = 1 AND `code` = 'MC82';

INSERT INTO `SERVICE_PRICES` (`service_id`,`hospital_id`,`price`,`currency`,`payer_type`,`area_tag`,`effective_from`,`effective_to`,`notes`,`status`)
SELECT `service_id`, 1, 150000.00, 'VND', 'TU_CHI_TRA', NULL, '2024-01-01', NULL, NULL, 1
FROM `SERVICES`
WHERE `hospital_id` = 1 AND `code` = 'MC89';

INSERT INTO `SERVICE_PRICES` (`service_id`,`hospital_id`,`price`,`currency`,`payer_type`,`area_tag`,`effective_from`,`effective_to`,`notes`,`status`)
SELECT `service_id`, 1, 58600.00, 'VND', 'BHYT', NULL, '2024-01-01', NULL, NULL, 1
FROM `SERVICES`
WHERE `hospital_id` = 1 AND `code` = 'MC89';

INSERT INTO `SERVICE_PRICES` (`service_id`,`hospital_id`,`price`,`currency`,`payer_type`,`area_tag`,`effective_from`,`effective_to`,`notes`,`status`)
SELECT `service_id`, 1, 400000.00, 'VND', 'TU_CHI_TRA', NULL, '2024-01-01', NULL, NULL, 1
FROM `SERVICES`
WHERE `hospital_id` = 1 AND `code` = 'MC95';

INSERT INTO `SERVICE_PRICES` (`service_id`,`hospital_id`,`price`,`currency`,`payer_type`,`area_tag`,`effective_from`,`effective_to`,`notes`,`status`)
SELECT `service_id`, 1, 252300.00, 'VND', 'BHYT', NULL, '2024-01-01', NULL, NULL, 1
FROM `SERVICES`
WHERE `hospital_id` = 1 AND `code` = 'MC95';

INSERT INTO `SERVICE_PRICES` (`service_id`,`hospital_id`,`price`,`currency`,`payer_type`,`area_tag`,`effective_from`,`effective_to`,`notes`,`status`)
SELECT `service_id`, 1, 150000.00, 'VND', 'TU_CHI_TRA', NULL, '2024-01-01', NULL, NULL, 1
FROM `SERVICES`
WHERE `hospital_id` = 1 AND `code` = 'MCA5';

INSERT INTO `SERVICE_PRICES` (`service_id`,`hospital_id`,`price`,`currency`,`payer_type`,`area_tag`,`effective_from`,`effective_to`,`notes`,`status`)
SELECT `service_id`, 1, 58600.00, 'VND', 'BHYT', NULL, '2024-01-01', NULL, NULL, 1
FROM `SERVICES`
WHERE `hospital_id` = 1 AND `code` = 'MCA5';

INSERT INTO `SERVICE_PRICES` (`service_id`,`hospital_id`,`price`,`currency`,`payer_type`,`area_tag`,`effective_from`,`effective_to`,`notes`,`status`)
SELECT `service_id`, 1, 350000.00, 'VND', 'TU_CHI_TRA', NULL, '2024-01-01', NULL, NULL, 1
FROM `SERVICES`
WHERE `hospital_id` = 1 AND `code` = 'MD18';

INSERT INTO `SERVICE_PRICES` (`service_id`,`hospital_id`,`price`,`currency`,`payer_type`,`area_tag`,`effective_from`,`effective_to`,`notes`,`status`)
SELECT `service_id`, 1, 252300.00, 'VND', 'BHYT', NULL, '2024-01-01', NULL, NULL, 1
FROM `SERVICES`
WHERE `hospital_id` = 1 AND `code` = 'MD18';

INSERT INTO `SERVICE_PRICES` (`service_id`,`hospital_id`,`price`,`currency`,`payer_type`,`area_tag`,`effective_from`,`effective_to`,`notes`,`status`)
SELECT `service_id`, 1, 450000.00, 'VND', 'TU_CHI_TRA', NULL, '2024-01-01', NULL, NULL, 1
FROM `SERVICES`
WHERE `hospital_id` = 1 AND `code` = 'MD19';

INSERT INTO `SERVICE_PRICES` (`service_id`,`hospital_id`,`price`,`currency`,`payer_type`,`area_tag`,`effective_from`,`effective_to`,`notes`,`status`)
SELECT `service_id`, 1, 252300.00, 'VND', 'BHYT', NULL, '2024-01-01', NULL, NULL, 1
FROM `SERVICES`
WHERE `hospital_id` = 1 AND `code` = 'MD19';

INSERT INTO `SERVICE_PRICES` (`service_id`,`hospital_id`,`price`,`currency`,`payer_type`,`area_tag`,`effective_from`,`effective_to`,`notes`,`status`)
SELECT `service_id`, 1, 280000.00, 'VND', 'TU_CHI_TRA', NULL, '2024-01-01', NULL, NULL, 1
FROM `SERVICES`
WHERE `hospital_id` = 1 AND `code` = 'MD08';

INSERT INTO `SERVICE_PRICES` (`service_id`,`hospital_id`,`price`,`currency`,`payer_type`,`area_tag`,`effective_from`,`effective_to`,`notes`,`status`)
SELECT `service_id`, 1, 252300.00, 'VND', 'BHYT', NULL, '2024-01-01', NULL, NULL, 1
FROM `SERVICES`
WHERE `hospital_id` = 1 AND `code` = 'MD08';

INSERT INTO `SERVICE_PRICES` (`service_id`,`hospital_id`,`price`,`currency`,`payer_type`,`area_tag`,`effective_from`,`effective_to`,`notes`,`status`)
SELECT `service_id`, 1, 1950000.00, 'VND', 'TU_CHI_TRA', NULL, '2024-01-01', NULL, NULL, 1
FROM `SERVICES`
WHERE `hospital_id` = 1 AND `code` = 'ND91';

INSERT INTO `SERVICE_PRICES` (`service_id`,`hospital_id`,`price`,`currency`,`payer_type`,`area_tag`,`effective_from`,`effective_to`,`notes`,`status`)
SELECT `service_id`, 1, 663400.00, 'VND', 'BHYT', NULL, '2024-01-01', NULL, NULL, 1
FROM `SERVICES`
WHERE `hospital_id` = 1 AND `code` = 'ND91';

INSERT INTO `SERVICE_PRICES` (`service_id`,`hospital_id`,`price`,`currency`,`payer_type`,`area_tag`,`effective_from`,`effective_to`,`notes`,`status`)
SELECT `service_id`, 1, 1000000.00, 'VND', 'TU_CHI_TRA', NULL, '2024-01-01', NULL, NULL, 1
FROM `SERVICES`
WHERE `hospital_id` = 1 AND `code` = 'ND92';

INSERT INTO `SERVICE_PRICES` (`service_id`,`hospital_id`,`price`,`currency`,`payer_type`,`area_tag`,`effective_from`,`effective_to`,`notes`,`status`)
SELECT `service_id`, 1, 550100.00, 'VND', 'BHYT', NULL, '2024-01-01', NULL, NULL, 1
FROM `SERVICES`
WHERE `hospital_id` = 1 AND `code` = 'ND92';

INSERT INTO `SERVICE_PRICES` (`service_id`,`hospital_id`,`price`,`currency`,`payer_type`,`area_tag`,`effective_from`,`effective_to`,`notes`,`status`)
SELECT `service_id`, 1, 1240000.00, 'VND', 'TU_CHI_TRA', NULL, '2024-01-01', NULL, NULL, 1
FROM `SERVICES`
WHERE `hospital_id` = 1 AND `code` = 'ND93';

INSERT INTO `SERVICE_PRICES` (`service_id`,`hospital_id`,`price`,`currency`,`payer_type`,`area_tag`,`effective_from`,`effective_to`,`notes`,`status`)
SELECT `service_id`, 1, 663400.00, 'VND', 'BHYT', NULL, '2024-01-01', NULL, NULL, 1
FROM `SERVICES`
WHERE `hospital_id` = 1 AND `code` = 'ND93';

INSERT INTO `SERVICE_PRICES` (`service_id`,`hospital_id`,`price`,`currency`,`payer_type`,`area_tag`,`effective_from`,`effective_to`,`notes`,`status`)
SELECT `service_id`, 1, 1000000.00, 'VND', 'TU_CHI_TRA', NULL, '2024-01-01', NULL, NULL, 1
FROM `SERVICES`
WHERE `hospital_id` = 1 AND `code` = 'ND94';

INSERT INTO `SERVICE_PRICES` (`service_id`,`hospital_id`,`price`,`currency`,`payer_type`,`area_tag`,`effective_from`,`effective_to`,`notes`,`status`)
SELECT `service_id`, 1, 550100.00, 'VND', 'BHYT', NULL, '2024-01-01', NULL, NULL, 1
FROM `SERVICES`
WHERE `hospital_id` = 1 AND `code` = 'ND94';

INSERT INTO `SERVICE_PRICES` (`service_id`,`hospital_id`,`price`,`currency`,`payer_type`,`area_tag`,`effective_from`,`effective_to`,`notes`,`status`)
SELECT `service_id`, 1, 1240000.00, 'VND', 'TU_CHI_TRA', NULL, '2024-01-01', NULL, NULL, 1
FROM `SERVICES`
WHERE `hospital_id` = 1 AND `code` = 'ND95';

INSERT INTO `SERVICE_PRICES` (`service_id`,`hospital_id`,`price`,`currency`,`payer_type`,`area_tag`,`effective_from`,`effective_to`,`notes`,`status`)
SELECT `service_id`, 1, 663400.00, 'VND', 'BHYT', NULL, '2024-01-01', NULL, NULL, 1
FROM `SERVICES`
WHERE `hospital_id` = 1 AND `code` = 'ND95';

INSERT INTO `SERVICE_PRICES` (`service_id`,`hospital_id`,`price`,`currency`,`payer_type`,`area_tag`,`effective_from`,`effective_to`,`notes`,`status`)
SELECT `service_id`, 1, 1000000.00, 'VND', 'TU_CHI_TRA', NULL, '2024-01-01', NULL, NULL, 1
FROM `SERVICES`
WHERE `hospital_id` = 1 AND `code` = 'ND96';

INSERT INTO `SERVICE_PRICES` (`service_id`,`hospital_id`,`price`,`currency`,`payer_type`,`area_tag`,`effective_from`,`effective_to`,`notes`,`status`)
SELECT `service_id`, 1, 550100.00, 'VND', 'BHYT', NULL, '2024-01-01', NULL, NULL, 1
FROM `SERVICES`
WHERE `hospital_id` = 1 AND `code` = 'ND96';

INSERT INTO `SERVICE_PRICES` (`service_id`,`hospital_id`,`price`,`currency`,`payer_type`,`area_tag`,`effective_from`,`effective_to`,`notes`,`status`)
SELECT `service_id`, 1, 1240000.00, 'VND', 'TU_CHI_TRA', NULL, '2024-01-01', NULL, NULL, 1
FROM `SERVICES`
WHERE `hospital_id` = 1 AND `code` = 'ND97';

INSERT INTO `SERVICE_PRICES` (`service_id`,`hospital_id`,`price`,`currency`,`payer_type`,`area_tag`,`effective_from`,`effective_to`,`notes`,`status`)
SELECT `service_id`, 1, 663400.00, 'VND', 'BHYT', NULL, '2024-01-01', NULL, NULL, 1
FROM `SERVICES`
WHERE `hospital_id` = 1 AND `code` = 'ND97';

INSERT INTO `SERVICE_PRICES` (`service_id`,`hospital_id`,`price`,`currency`,`payer_type`,`area_tag`,`effective_from`,`effective_to`,`notes`,`status`)
SELECT `service_id`, 1, 100000.00, 'VND', 'TU_CHI_TRA', NULL, '2024-01-01', NULL, NULL, 1
FROM `SERVICES`
WHERE `hospital_id` = 1 AND `code` = 'MAA4';

INSERT INTO `SERVICE_PRICES` (`service_id`,`hospital_id`,`price`,`currency`,`payer_type`,`area_tag`,`effective_from`,`effective_to`,`notes`,`status`)
SELECT `service_id`, 1, 73300.00, 'VND', 'BHYT', NULL, '2024-01-01', NULL, NULL, 1
FROM `SERVICES`
WHERE `hospital_id` = 1 AND `code` = 'MAA4';

INSERT INTO `SERVICE_PRICES` (`service_id`,`hospital_id`,`price`,`currency`,`payer_type`,`area_tag`,`effective_from`,`effective_to`,`notes`,`status`)
SELECT `service_id`, 1, 100000.00, 'VND', 'TU_CHI_TRA', NULL, '2024-01-01', NULL, NULL, 1
FROM `SERVICES`
WHERE `hospital_id` = 1 AND `code` = 'MAA5';

INSERT INTO `SERVICE_PRICES` (`service_id`,`hospital_id`,`price`,`currency`,`payer_type`,`area_tag`,`effective_from`,`effective_to`,`notes`,`status`)
SELECT `service_id`, 1, 73300.00, 'VND', 'BHYT', NULL, '2024-01-01', NULL, NULL, 1
FROM `SERVICES`
WHERE `hospital_id` = 1 AND `code` = 'MAA5';

INSERT INTO `SERVICE_PRICES` (`service_id`,`hospital_id`,`price`,`currency`,`payer_type`,`area_tag`,`effective_from`,`effective_to`,`notes`,`status`)
SELECT `service_id`, 1, 130000.00, 'VND', 'TU_CHI_TRA', NULL, '2024-01-01', NULL, NULL, 1
FROM `SERVICES`
WHERE `hospital_id` = 1 AND `code` = 'MAA6';

INSERT INTO `SERVICE_PRICES` (`service_id`,`hospital_id`,`price`,`currency`,`payer_type`,`area_tag`,`effective_from`,`effective_to`,`notes`,`status`)
SELECT `service_id`, 1, 73300.00, 'VND', 'BHYT', NULL, '2024-01-01', NULL, NULL, 1
FROM `SERVICES`
WHERE `hospital_id` = 1 AND `code` = 'MAA6';

INSERT INTO `SERVICE_PRICES` (`service_id`,`hospital_id`,`price`,`currency`,`payer_type`,`area_tag`,`effective_from`,`effective_to`,`notes`,`status`)
SELECT `service_id`, 1, 100000.00, 'VND', 'TU_CHI_TRA', NULL, '2024-01-01', NULL, NULL, 1
FROM `SERVICES`
WHERE `hospital_id` = 1 AND `code` = 'MAB0';

INSERT INTO `SERVICE_PRICES` (`service_id`,`hospital_id`,`price`,`currency`,`payer_type`,`area_tag`,`effective_from`,`effective_to`,`notes`,`status`)
SELECT `service_id`, 1, 73300.00, 'VND', 'BHYT', NULL, '2024-01-01', NULL, NULL, 1
FROM `SERVICES`
WHERE `hospital_id` = 1 AND `code` = 'MAB0';

INSERT INTO `SERVICE_PRICES` (`service_id`,`hospital_id`,`price`,`currency`,`payer_type`,`area_tag`,`effective_from`,`effective_to`,`notes`,`status`)
SELECT `service_id`, 1, 130000.00, 'VND', 'TU_CHI_TRA', NULL, '2024-01-01', NULL, NULL, 1
FROM `SERVICES`
WHERE `hospital_id` = 1 AND `code` = 'MAC7';

INSERT INTO `SERVICE_PRICES` (`service_id`,`hospital_id`,`price`,`currency`,`payer_type`,`area_tag`,`effective_from`,`effective_to`,`notes`,`status`)
SELECT `service_id`, 1, 73300.00, 'VND', 'BHYT', NULL, '2024-01-01', NULL, NULL, 1
FROM `SERVICES`
WHERE `hospital_id` = 1 AND `code` = 'MAC7';

INSERT INTO `SERVICE_PRICES` (`service_id`,`hospital_id`,`price`,`currency`,`payer_type`,`area_tag`,`effective_from`,`effective_to`,`notes`,`status`)
SELECT `service_id`, 1, 130000.00, 'VND', 'TU_CHI_TRA', NULL, '2024-01-01', NULL, NULL, 1
FROM `SERVICES`
WHERE `hospital_id` = 1 AND `code` = 'MAD1';

INSERT INTO `SERVICE_PRICES` (`service_id`,`hospital_id`,`price`,`currency`,`payer_type`,`area_tag`,`effective_from`,`effective_to`,`notes`,`status`)
SELECT `service_id`, 1, 73300.00, 'VND', 'BHYT', NULL, '2024-01-01', NULL, NULL, 1
FROM `SERVICES`
WHERE `hospital_id` = 1 AND `code` = 'MAD1';

INSERT INTO `SERVICE_PRICES` (`service_id`,`hospital_id`,`price`,`currency`,`payer_type`,`area_tag`,`effective_from`,`effective_to`,`notes`,`status`)
SELECT `service_id`, 1, 130000.00, 'VND', 'TU_CHI_TRA', NULL, '2024-01-01', NULL, NULL, 1
FROM `SERVICES`
WHERE `hospital_id` = 1 AND `code` = 'MAD5';

INSERT INTO `SERVICE_PRICES` (`service_id`,`hospital_id`,`price`,`currency`,`payer_type`,`area_tag`,`effective_from`,`effective_to`,`notes`,`status`)
SELECT `service_id`, 1, 73300.00, 'VND', 'BHYT', NULL, '2024-01-01', NULL, NULL, 1
FROM `SERVICES`
WHERE `hospital_id` = 1 AND `code` = 'MAD5';

INSERT INTO `SERVICE_PRICES` (`service_id`,`hospital_id`,`price`,`currency`,`payer_type`,`area_tag`,`effective_from`,`effective_to`,`notes`,`status`)
SELECT `service_id`, 1, 33000.00, 'VND', 'TU_CHI_TRA', NULL, '2024-01-01', NULL, NULL, 1
FROM `SERVICES`
WHERE `hospital_id` = 1 AND `code` = 'MH45';

INSERT INTO `SERVICE_PRICES` (`service_id`,`hospital_id`,`price`,`currency`,`payer_type`,`area_tag`,`effective_from`,`effective_to`,`notes`,`status`)
SELECT `service_id`, 1, 28000.00, 'VND', 'BHYT', NULL, '2024-01-01', NULL, NULL, 1
FROM `SERVICES`
WHERE `hospital_id` = 1 AND `code` = 'MH45';

INSERT INTO `SERVICE_PRICES` (`service_id`,`hospital_id`,`price`,`currency`,`payer_type`,`area_tag`,`effective_from`,`effective_to`,`notes`,`status`)
SELECT `service_id`, 1, 76500.00, 'VND', 'TU_CHI_TRA', NULL, '2024-01-01', NULL, NULL, 1
FROM `SERVICES`
WHERE `hospital_id` = 1 AND `code` = 'MH46';

INSERT INTO `SERVICE_PRICES` (`service_id`,`hospital_id`,`price`,`currency`,`payer_type`,`area_tag`,`effective_from`,`effective_to`,`notes`,`status`)
SELECT `service_id`, 1, 76500.00, 'VND', 'BHYT', NULL, '2024-01-01', NULL, NULL, 1
FROM `SERVICES`
WHERE `hospital_id` = 1 AND `code` = 'MH46';

INSERT INTO `SERVICE_PRICES` (`service_id`,`hospital_id`,`price`,`currency`,`payer_type`,`area_tag`,`effective_from`,`effective_to`,`notes`,`status`)
SELECT `service_id`, 1, 43000.00, 'VND', 'TU_CHI_TRA', NULL, '2024-01-01', NULL, NULL, 1
FROM `SERVICES`
WHERE `hospital_id` = 1 AND `code` = 'MH47';

INSERT INTO `SERVICE_PRICES` (`service_id`,`hospital_id`,`price`,`currency`,`payer_type`,`area_tag`,`effective_from`,`effective_to`,`notes`,`status`)
SELECT `service_id`, 1, 16800.00, 'VND', 'BHYT', NULL, '2024-01-01', NULL, NULL, 1
FROM `SERVICES`
WHERE `hospital_id` = 1 AND `code` = 'MH47';

INSERT INTO `SERVICE_PRICES` (`service_id`,`hospital_id`,`price`,`currency`,`payer_type`,`area_tag`,`effective_from`,`effective_to`,`notes`,`status`)
SELECT `service_id`, 1, 48000.00, 'VND', 'TU_CHI_TRA', NULL, '2024-01-01', NULL, NULL, 1
FROM `SERVICES`
WHERE `hospital_id` = 1 AND `code` = 'MH51';

INSERT INTO `SERVICE_PRICES` (`service_id`,`hospital_id`,`price`,`currency`,`payer_type`,`area_tag`,`effective_from`,`effective_to`,`notes`,`status`)
SELECT `service_id`, 1, 39200.00, 'VND', 'BHYT', NULL, '2024-01-01', NULL, NULL, 1
FROM `SERVICES`
WHERE `hospital_id` = 1 AND `code` = 'MH51';

INSERT INTO `SERVICE_PRICES` (`service_id`,`hospital_id`,`price`,`currency`,`payer_type`,`area_tag`,`effective_from`,`effective_to`,`notes`,`status`)
SELECT `service_id`, 1, 65600.00, 'VND', 'TU_CHI_TRA', NULL, '2024-01-01', NULL, NULL, 1
FROM `SERVICES`
WHERE `hospital_id` = 1 AND `code` = 'MH52';

INSERT INTO `SERVICE_PRICES` (`service_id`,`hospital_id`,`price`,`currency`,`payer_type`,`area_tag`,`effective_from`,`effective_to`,`notes`,`status`)
SELECT `service_id`, 1, 65600.00, 'VND', 'BHYT', NULL, '2024-01-01', NULL, NULL, 1
FROM `SERVICES`
WHERE `hospital_id` = 1 AND `code` = 'MH52';

INSERT INTO `SERVICE_PRICES` (`service_id`,`hospital_id`,`price`,`currency`,`payer_type`,`area_tag`,`effective_from`,`effective_to`,`notes`,`status`)
SELECT `service_id`, 1, 25000.00, 'VND', 'TU_CHI_TRA', NULL, '2024-01-01', NULL, NULL, 1
FROM `SERVICES`
WHERE `hospital_id` = 1 AND `code` = 'MH26';

INSERT INTO `SERVICE_PRICES` (`service_id`,`hospital_id`,`price`,`currency`,`payer_type`,`area_tag`,`effective_from`,`effective_to`,`notes`,`status`)
SELECT `service_id`, 1, 22400.00, 'VND', 'BHYT', NULL, '2024-01-01', NULL, NULL, 1
FROM `SERVICES`
WHERE `hospital_id` = 1 AND `code` = 'MH26';

INSERT INTO `SERVICE_PRICES` (`service_id`,`hospital_id`,`price`,`currency`,`payer_type`,`area_tag`,`effective_from`,`effective_to`,`notes`,`status`)
SELECT `service_id`, 1, 55000.00, 'VND', 'TU_CHI_TRA', NULL, '2024-01-01', NULL, NULL, 1
FROM `SERVICES`
WHERE `hospital_id` = 1 AND `code` = 'MH27';

INSERT INTO `SERVICE_PRICES` (`service_id`,`hospital_id`,`price`,`currency`,`payer_type`,`area_tag`,`effective_from`,`effective_to`,`notes`,`status`)
SELECT `service_id`, 1, 45500.00, 'VND', 'BHYT', NULL, '2024-01-01', NULL, NULL, 1
FROM `SERVICES`
WHERE `hospital_id` = 1 AND `code` = 'MH27';

INSERT INTO `SERVICE_PRICES` (`service_id`,`hospital_id`,`price`,`currency`,`payer_type`,`area_tag`,`effective_from`,`effective_to`,`notes`,`status`)
SELECT `service_id`, 1, 51000.00, 'VND', 'TU_CHI_TRA', NULL, '2024-01-01', NULL, NULL, 1
FROM `SERVICES`
WHERE `hospital_id` = 1 AND `code` = 'MI29';

INSERT INTO `SERVICE_PRICES` (`service_id`,`hospital_id`,`price`,`currency`,`payer_type`,`area_tag`,`effective_from`,`effective_to`,`notes`,`status`)
SELECT `service_id`, 1, 43500.00, 'VND', 'BHYT', NULL, '2024-01-01', NULL, NULL, 1
FROM `SERVICES`
WHERE `hospital_id` = 1 AND `code` = 'MI29';

INSERT INTO `SERVICE_PRICES` (`service_id`,`hospital_id`,`price`,`currency`,`payer_type`,`area_tag`,`effective_from`,`effective_to`,`notes`,`status`)
SELECT `service_id`, 1, 73000.00, 'VND', 'TU_CHI_TRA', NULL, '2024-01-01', NULL, NULL, 1
FROM `SERVICES`
WHERE `hospital_id` = 1 AND `code` = 'MI35';

INSERT INTO `SERVICE_PRICES` (`service_id`,`hospital_id`,`price`,`currency`,`payer_type`,`area_tag`,`effective_from`,`effective_to`,`notes`,`status`)
SELECT `service_id`, 1, 45500.00, 'VND', 'BHYT', NULL, '2024-01-01', NULL, NULL, 1
FROM `SERVICES`
WHERE `hospital_id` = 1 AND `code` = 'MI35';

INSERT INTO `SERVICE_PRICES` (`service_id`,`hospital_id`,`price`,`currency`,`payer_type`,`area_tag`,`effective_from`,`effective_to`,`notes`,`status`)
SELECT `service_id`, 1, 160000.00, 'VND', 'TU_CHI_TRA', NULL, '2024-01-01', NULL, NULL, 1
FROM `SERVICES`
WHERE `hospital_id` = 1 AND `code` = 'MI42';

INSERT INTO `SERVICE_PRICES` (`service_id`,`hospital_id`,`price`,`currency`,`payer_type`,`area_tag`,`effective_from`,`effective_to`,`notes`,`status`)
SELECT `service_id`, 1, 74600.00, 'VND', 'BHYT', NULL, '2024-01-01', NULL, NULL, 1
FROM `SERVICES`
WHERE `hospital_id` = 1 AND `code` = 'MI42';

INSERT INTO `SERVICE_PRICES` (`service_id`,`hospital_id`,`price`,`currency`,`payer_type`,`area_tag`,`effective_from`,`effective_to`,`notes`,`status`)
SELECT `service_id`, 1, 458000.00, 'VND', 'TU_CHI_TRA', NULL, '2024-01-01', NULL, NULL, 1
FROM `SERVICES`
WHERE `hospital_id` = 1 AND `code` = 'MI45';

INSERT INTO `SERVICE_PRICES` (`service_id`,`hospital_id`,`price`,`currency`,`payer_type`,`area_tag`,`effective_from`,`effective_to`,`notes`,`status`)
SELECT `service_id`, 1, 272900.00, 'VND', 'BHYT', NULL, '2024-01-01', NULL, NULL, 1
FROM `SERVICES`
WHERE `hospital_id` = 1 AND `code` = 'MI45';

INSERT INTO `SERVICE_PRICES` (`service_id`,`hospital_id`,`price`,`currency`,`payer_type`,`area_tag`,`effective_from`,`effective_to`,`notes`,`status`)
SELECT `service_id`, 1, 188000.00, 'VND', 'TU_CHI_TRA', NULL, '2024-01-01', NULL, NULL, 1
FROM `SERVICES`
WHERE `hospital_id` = 1 AND `code` = 'MI48';

INSERT INTO `SERVICE_PRICES` (`service_id`,`hospital_id`,`price`,`currency`,`payer_type`,`area_tag`,`effective_from`,`effective_to`,`notes`,`status`)
SELECT `service_id`, 1, 42100.00, 'VND', 'BHYT', NULL, '2024-01-01', NULL, NULL, 1
FROM `SERVICES`
WHERE `hospital_id` = 1 AND `code` = 'MI48';

INSERT INTO `SERVICE_PRICES` (`service_id`,`hospital_id`,`price`,`currency`,`payer_type`,`area_tag`,`effective_from`,`effective_to`,`notes`,`status`)
SELECT `service_id`, 1, 162000.00, 'VND', 'TU_CHI_TRA', NULL, '2024-01-01', NULL, NULL, 1
FROM `SERVICES`
WHERE `hospital_id` = 1 AND `code` = 'MJ57';

INSERT INTO `SERVICE_PRICES` (`service_id`,`hospital_id`,`price`,`currency`,`payer_type`,`area_tag`,`effective_from`,`effective_to`,`notes`,`status`)
SELECT `service_id`, 1, 84100.00, 'VND', 'BHYT', NULL, '2024-01-01', NULL, NULL, 1
FROM `SERVICES`
WHERE `hospital_id` = 1 AND `code` = 'MJ57';

INSERT INTO `SERVICE_PRICES` (`service_id`,`hospital_id`,`price`,`currency`,`payer_type`,`area_tag`,`effective_from`,`effective_to`,`notes`,`status`)
SELECT `service_id`, 1, 184000.00, 'VND', 'TU_CHI_TRA', NULL, '2024-01-01', NULL, NULL, 1
FROM `SERVICES`
WHERE `hospital_id` = 1 AND `code` = 'MJ63';

INSERT INTO `SERVICE_PRICES` (`service_id`,`hospital_id`,`price`,`currency`,`payer_type`,`area_tag`,`effective_from`,`effective_to`,`notes`,`status`)
SELECT `service_id`, 1, 144200.00, 'VND', 'BHYT', NULL, '2024-01-01', NULL, NULL, 1
FROM `SERVICES`
WHERE `hospital_id` = 1 AND `code` = 'MJ63';

INSERT INTO `SERVICE_PRICES` (`service_id`,`hospital_id`,`price`,`currency`,`payer_type`,`area_tag`,`effective_from`,`effective_to`,`notes`,`status`)
SELECT `service_id`, 1, 166000.00, 'VND', 'TU_CHI_TRA', NULL, '2024-01-01', NULL, NULL, 1
FROM `SERVICES`
WHERE `hospital_id` = 1 AND `code` = 'MJ64';

INSERT INTO `SERVICE_PRICES` (`service_id`,`hospital_id`,`price`,`currency`,`payer_type`,`area_tag`,`effective_from`,`effective_to`,`notes`,`status`)
SELECT `service_id`, 1, 123400.00, 'VND', 'BHYT', NULL, '2024-01-01', NULL, NULL, 1
FROM `SERVICES`
WHERE `hospital_id` = 1 AND `code` = 'MJ64';

INSERT INTO `SERVICE_PRICES` (`service_id`,`hospital_id`,`price`,`currency`,`payer_type`,`area_tag`,`effective_from`,`effective_to`,`notes`,`status`)
SELECT `service_id`, 1, 184000.00, 'VND', 'TU_CHI_TRA', NULL, '2024-01-01', NULL, NULL, 1
FROM `SERVICES`
WHERE `hospital_id` = 1 AND `code` = 'MJ65';

INSERT INTO `SERVICE_PRICES` (`service_id`,`hospital_id`,`price`,`currency`,`payer_type`,`area_tag`,`effective_from`,`effective_to`,`notes`,`status`)
SELECT `service_id`, 1, 116400.00, 'VND', 'BHYT', NULL, '2024-01-01', NULL, NULL, 1
FROM `SERVICES`
WHERE `hospital_id` = 1 AND `code` = 'MJ65';

INSERT INTO `SERVICE_PRICES` (`service_id`,`hospital_id`,`price`,`currency`,`payer_type`,`area_tag`,`effective_from`,`effective_to`,`notes`,`status`)
SELECT `service_id`, 1, 161000.00, 'VND', 'TU_CHI_TRA', NULL, '2024-01-01', NULL, NULL, 1
FROM `SERVICES`
WHERE `hospital_id` = 1 AND `code` = 'MJ66';

INSERT INTO `SERVICE_PRICES` (`service_id`,`hospital_id`,`price`,`currency`,`payer_type`,`area_tag`,`effective_from`,`effective_to`,`notes`,`status`)
SELECT `service_id`, 1, 110800.00, 'VND', 'BHYT', NULL, '2024-01-01', NULL, NULL, 1
FROM `SERVICES`
WHERE `hospital_id` = 1 AND `code` = 'MJ66';

INSERT INTO `SERVICE_PRICES` (`service_id`,`hospital_id`,`price`,`currency`,`payer_type`,`area_tag`,`effective_from`,`effective_to`,`notes`,`status`)
SELECT `service_id`, 1, 2000000.00, 'VND', 'TU_CHI_TRA', NULL, '2024-01-01', NULL, NULL, 1
FROM `SERVICES`
WHERE `hospital_id` = 1 AND `code` = 'MB82';

INSERT INTO `SERVICE_PRICES` (`service_id`,`hospital_id`,`price`,`currency`,`payer_type`,`area_tag`,`effective_from`,`effective_to`,`notes`,`status`)
SELECT `service_id`, 1, 1743100.00, 'VND', 'BHYT', NULL, '2024-01-01', NULL, NULL, 1
FROM `SERVICES`
WHERE `hospital_id` = 1 AND `code` = 'MB82';

INSERT INTO `SERVICE_PRICES` (`service_id`,`hospital_id`,`price`,`currency`,`payer_type`,`area_tag`,`effective_from`,`effective_to`,`notes`,`status`)
SELECT `service_id`, 1, 800000.00, 'VND', 'TU_CHI_TRA', NULL, '2024-01-01', NULL, NULL, 1
FROM `SERVICES`
WHERE `hospital_id` = 1 AND `code` = 'MBB3';

INSERT INTO `SERVICE_PRICES` (`service_id`,`hospital_id`,`price`,`currency`,`payer_type`,`area_tag`,`effective_from`,`effective_to`,`notes`,`status`)
SELECT `service_id`, 1, 493800.00, 'VND', 'BHYT', NULL, '2024-01-01', NULL, NULL, 1
FROM `SERVICES`
WHERE `hospital_id` = 1 AND `code` = 'MBB3';

INSERT INTO `SERVICE_PRICES` (`service_id`,`hospital_id`,`price`,`currency`,`payer_type`,`area_tag`,`effective_from`,`effective_to`,`notes`,`status`)
SELECT `service_id`, 1, 550000.00, 'VND', 'TU_CHI_TRA', NULL, '2024-01-01', NULL, NULL, 1
FROM `SERVICES`
WHERE `hospital_id` = 1 AND `code` = 'MBB4';

INSERT INTO `SERVICE_PRICES` (`service_id`,`hospital_id`,`price`,`currency`,`payer_type`,`area_tag`,`effective_from`,`effective_to`,`notes`,`status`)
SELECT `service_id`, 1, 215200.00, 'VND', 'BHYT', NULL, '2024-01-01', NULL, NULL, 1
FROM `SERVICES`
WHERE `hospital_id` = 1 AND `code` = 'MBB4';

INSERT INTO `SERVICE_PRICES` (`service_id`,`hospital_id`,`price`,`currency`,`payer_type`,`area_tag`,`effective_from`,`effective_to`,`notes`,`status`)
SELECT `service_id`, 1, 450000.00, 'VND', 'TU_CHI_TRA', NULL, '2024-01-01', NULL, NULL, 1
FROM `SERVICES`
WHERE `hospital_id` = 1 AND `code` = 'MBB5';

INSERT INTO `SERVICE_PRICES` (`service_id`,`hospital_id`,`price`,`currency`,`payer_type`,`area_tag`,`effective_from`,`effective_to`,`notes`,`status`)
SELECT `service_id`, 1, 215200.00, 'VND', 'BHYT', NULL, '2024-01-01', NULL, NULL, 1
FROM `SERVICES`
WHERE `hospital_id` = 1 AND `code` = 'MBB5';

INSERT INTO `SERVICE_PRICES` (`service_id`,`hospital_id`,`price`,`currency`,`payer_type`,`area_tag`,`effective_from`,`effective_to`,`notes`,`status`)
SELECT `service_id`, 1, 3400000.00, 'VND', 'TU_CHI_TRA', NULL, '2024-01-01', NULL, NULL, 1
FROM `SERVICES`
WHERE `hospital_id` = 1 AND `code` = 'MBH6';

INSERT INTO `SERVICE_PRICES` (`service_id`,`hospital_id`,`price`,`currency`,`payer_type`,`area_tag`,`effective_from`,`effective_to`,`notes`,`status`)
SELECT `service_id`, 1, 1108300.00, 'VND', 'BHYT', NULL, '2024-01-01', NULL, NULL, 1
FROM `SERVICES`
WHERE `hospital_id` = 1 AND `code` = 'MBH6';

INSERT INTO `SERVICE_PRICES` (`service_id`,`hospital_id`,`price`,`currency`,`payer_type`,`area_tag`,`effective_from`,`effective_to`,`notes`,`status`)
SELECT `service_id`, 1, 270000.00, 'VND', 'TU_CHI_TRA', NULL, '2024-01-01', NULL, NULL, 1
FROM `SERVICES`
WHERE `hospital_id` = 1 AND `code` = 'TZ01';

INSERT INTO `SERVICE_PRICES` (`service_id`,`hospital_id`,`price`,`currency`,`payer_type`,`area_tag`,`effective_from`,`effective_to`,`notes`,`status`)
SELECT `service_id`, 1, 116100.00, 'VND', 'BHYT', NULL, '2024-01-01', NULL, NULL, 1
FROM `SERVICES`
WHERE `hospital_id` = 1 AND `code` = 'TZ01';

INSERT INTO `SERVICE_PRICES` (`service_id`,`hospital_id`,`price`,`currency`,`payer_type`,`area_tag`,`effective_from`,`effective_to`,`notes`,`status`)
SELECT `service_id`, 1, 100000.00, 'VND', 'TU_CHI_TRA', NULL, '2024-01-01', NULL, NULL, 1
FROM `SERVICES`
WHERE `hospital_id` = 1 AND `code` = 'TZ02';

INSERT INTO `SERVICE_PRICES` (`service_id`,`hospital_id`,`price`,`currency`,`payer_type`,`area_tag`,`effective_from`,`effective_to`,`notes`,`status`)
SELECT `service_id`, 1, 40000.00, 'VND', 'BHYT', NULL, '2024-01-01', NULL, NULL, 1
FROM `SERVICES`
WHERE `hospital_id` = 1 AND `code` = 'TZ02';

INSERT INTO `SERVICE_PRICES` (`service_id`,`hospital_id`,`price`,`currency`,`payer_type`,`area_tag`,`effective_from`,`effective_to`,`notes`,`status`)
SELECT `service_id`, 1, 100000.00, 'VND', 'TU_CHI_TRA', NULL, '2024-01-01', NULL, NULL, 1
FROM `SERVICES`
WHERE `hospital_id` = 1 AND `code` = 'TZ03';

INSERT INTO `SERVICE_PRICES` (`service_id`,`hospital_id`,`price`,`currency`,`payer_type`,`area_tag`,`effective_from`,`effective_to`,`notes`,`status`)
SELECT `service_id`, 1, 40000.00, 'VND', 'BHYT', NULL, '2024-01-01', NULL, NULL, 1
FROM `SERVICES`
WHERE `hospital_id` = 1 AND `code` = 'TZ03';

INSERT INTO `SERVICE_PRICES` (`service_id`,`hospital_id`,`price`,`currency`,`payer_type`,`area_tag`,`effective_from`,`effective_to`,`notes`,`status`)
SELECT `service_id`, 1, 100000.00, 'VND', 'TU_CHI_TRA', NULL, '2024-01-01', NULL, NULL, 1
FROM `SERVICES`
WHERE `hospital_id` = 1 AND `code` = 'TZ04';

INSERT INTO `SERVICE_PRICES` (`service_id`,`hospital_id`,`price`,`currency`,`payer_type`,`area_tag`,`effective_from`,`effective_to`,`notes`,`status`)
SELECT `service_id`, 1, 40000.00, 'VND', 'BHYT', NULL, '2024-01-01', NULL, NULL, 1
FROM `SERVICES`
WHERE `hospital_id` = 1 AND `code` = 'TZ04';

INSERT INTO `SERVICE_PRICES` (`service_id`,`hospital_id`,`price`,`currency`,`payer_type`,`area_tag`,`effective_from`,`effective_to`,`notes`,`status`)
SELECT `service_id`, 1, 11000000.00, 'VND', 'TU_CHI_TRA', NULL, '2024-01-01', NULL, NULL, 1
FROM `SERVICES`
WHERE `hospital_id` = 1 AND `code` = 'N108';

INSERT INTO `SERVICE_PRICES` (`service_id`,`hospital_id`,`price`,`currency`,`payer_type`,`area_tag`,`effective_from`,`effective_to`,`notes`,`status`)
SELECT `service_id`, 1, 3226900.00, 'VND', 'BHYT', NULL, '2024-01-01', NULL, NULL, 1
FROM `SERVICES`
WHERE `hospital_id` = 1 AND `code` = 'N108';

INSERT INTO `SERVICE_PRICES` (`service_id`,`hospital_id`,`price`,`currency`,`payer_type`,`area_tag`,`effective_from`,`effective_to`,`notes`,`status`)
SELECT `service_id`, 1, 8200000.00, 'VND', 'TU_CHI_TRA', NULL, '2024-01-01', NULL, NULL, 1
FROM `SERVICES`
WHERE `hospital_id` = 1 AND `code` = 'N120';

INSERT INTO `SERVICE_PRICES` (`service_id`,`hospital_id`,`price`,`currency`,`payer_type`,`area_tag`,`effective_from`,`effective_to`,`notes`,`status`)
SELECT `service_id`, 1, 3923600.00, 'VND', 'BHYT', NULL, '2024-01-01', NULL, NULL, 1
FROM `SERVICES`
WHERE `hospital_id` = 1 AND `code` = 'N120';

INSERT INTO `SERVICE_PRICES` (`service_id`,`hospital_id`,`price`,`currency`,`payer_type`,`area_tag`,`effective_from`,`effective_to`,`notes`,`status`)
SELECT `service_id`, 1, 4600000.00, 'VND', 'TU_CHI_TRA', NULL, '2024-01-01', NULL, NULL, 1
FROM `SERVICES`
WHERE `hospital_id` = 1 AND `code` = 'N125';

INSERT INTO `SERVICE_PRICES` (`service_id`,`hospital_id`,`price`,`currency`,`payer_type`,`area_tag`,`effective_from`,`effective_to`,`notes`,`status`)
SELECT `service_id`, 1, 289500.00, 'VND', 'BHYT', NULL, '2024-01-01', NULL, NULL, 1
FROM `SERVICES`
WHERE `hospital_id` = 1 AND `code` = 'N125';

INSERT INTO `SERVICE_PRICES` (`service_id`,`hospital_id`,`price`,`currency`,`payer_type`,`area_tag`,`effective_from`,`effective_to`,`notes`,`status`)
SELECT `service_id`, 1, 1500000.00, 'VND', 'TU_CHI_TRA', NULL, '2024-01-01', NULL, NULL, 1
FROM `SERVICES`
WHERE `hospital_id` = 1 AND `code` = 'N128';

INSERT INTO `SERVICE_PRICES` (`service_id`,`hospital_id`,`price`,`currency`,`payer_type`,`area_tag`,`effective_from`,`effective_to`,`notes`,`status`)
SELECT `service_id`, 1, 659600.00, 'VND', 'BHYT', NULL, '2024-01-01', NULL, NULL, 1
FROM `SERVICES`
WHERE `hospital_id` = 1 AND `code` = 'N128';

INSERT INTO `SERVICE_PRICES` (`service_id`,`hospital_id`,`price`,`currency`,`payer_type`,`area_tag`,`effective_from`,`effective_to`,`notes`,`status`)
SELECT `service_id`, 1, 7100000.00, 'VND', 'TU_CHI_TRA', NULL, '2024-01-01', NULL, NULL, 1
FROM `SERVICES`
WHERE `hospital_id` = 1 AND `code` = 'L097';

INSERT INTO `SERVICE_PRICES` (`service_id`,`hospital_id`,`price`,`currency`,`payer_type`,`area_tag`,`effective_from`,`effective_to`,`notes`,`status`)
SELECT `service_id`, 1, 3628800.00, 'VND', 'BHYT', NULL, '2024-01-01', NULL, NULL, 1
FROM `SERVICES`
WHERE `hospital_id` = 1 AND `code` = 'L097';

INSERT INTO `SERVICE_PRICES` (`service_id`,`hospital_id`,`price`,`currency`,`payer_type`,`area_tag`,`effective_from`,`effective_to`,`notes`,`status`)
SELECT `service_id`, 1, 5100000.00, 'VND', 'TU_CHI_TRA', NULL, '2024-01-01', NULL, NULL, 1
FROM `SERVICES`
WHERE `hospital_id` = 1 AND `code` = 'L101';

INSERT INTO `SERVICE_PRICES` (`service_id`,`hospital_id`,`price`,`currency`,`payer_type`,`area_tag`,`effective_from`,`effective_to`,`notes`,`status`)
SELECT `service_id`, 1, 3019800.00, 'VND', 'BHYT', NULL, '2024-01-01', NULL, NULL, 1
FROM `SERVICES`
WHERE `hospital_id` = 1 AND `code` = 'L101';

INSERT INTO `SERVICE_PRICES` (`service_id`,`hospital_id`,`price`,`currency`,`payer_type`,`area_tag`,`effective_from`,`effective_to`,`notes`,`status`)
SELECT `service_id`, 1, 10700000.00, 'VND', 'TU_CHI_TRA', NULL, '2024-01-01', NULL, NULL, 1
FROM `SERVICES`
WHERE `hospital_id` = 1 AND `code` = 'L104';

INSERT INTO `SERVICE_PRICES` (`service_id`,`hospital_id`,`price`,`currency`,`payer_type`,`area_tag`,`effective_from`,`effective_to`,`notes`,`status`)
SELECT `service_id`, 1, 5503300.00, 'VND', 'BHYT', NULL, '2024-01-01', NULL, NULL, 1
FROM `SERVICES`
WHERE `hospital_id` = 1 AND `code` = 'L104';

INSERT INTO `SERVICE_PRICES` (`service_id`,`hospital_id`,`price`,`currency`,`payer_type`,`area_tag`,`effective_from`,`effective_to`,`notes`,`status`)
SELECT `service_id`, 1, 800000.00, 'VND', 'TU_CHI_TRA', NULL, '2024-01-01', NULL, NULL, 1
FROM `SERVICES`
WHERE `hospital_id` = 1 AND `code` = 'L106';

INSERT INTO `SERVICE_PRICES` (`service_id`,`hospital_id`,`price`,`currency`,`payer_type`,`area_tag`,`effective_from`,`effective_to`,`notes`,`status`)
SELECT `service_id`, 1, 436200.00, 'VND', 'BHYT', NULL, '2024-01-01', NULL, NULL, 1
FROM `SERVICES`
WHERE `hospital_id` = 1 AND `code` = 'L106';

INSERT INTO `SERVICE_PRICES` (`service_id`,`hospital_id`,`price`,`currency`,`payer_type`,`area_tag`,`effective_from`,`effective_to`,`notes`,`status`)
SELECT `service_id`, 1, 11300000.00, 'VND', 'TU_CHI_TRA', NULL, '2024-01-01', NULL, NULL, 1
FROM `SERVICES`
WHERE `hospital_id` = 1 AND `code` = 'H183';

INSERT INTO `SERVICE_PRICES` (`service_id`,`hospital_id`,`price`,`currency`,`payer_type`,`area_tag`,`effective_from`,`effective_to`,`notes`,`status`)
SELECT `service_id`, 1, 1010000.00, 'VND', 'BHYT', NULL, '2024-01-01', NULL, NULL, 1
FROM `SERVICES`
WHERE `hospital_id` = 1 AND `code` = 'H183';

INSERT INTO `SERVICE_PRICES` (`service_id`,`hospital_id`,`price`,`currency`,`payer_type`,`area_tag`,`effective_from`,`effective_to`,`notes`,`status`)
SELECT `service_id`, 1, 6700000.00, 'VND', 'TU_CHI_TRA', NULL, '2024-01-01', NULL, NULL, 1
FROM `SERVICES`
WHERE `hospital_id` = 1 AND `code` = 'H189';

INSERT INTO `SERVICE_PRICES` (`service_id`,`hospital_id`,`price`,`currency`,`payer_type`,`area_tag`,`effective_from`,`effective_to`,`notes`,`status`)
SELECT `service_id`, 1, 953800.00, 'VND', 'BHYT', NULL, '2024-01-01', NULL, NULL, 1
FROM `SERVICES`
WHERE `hospital_id` = 1 AND `code` = 'H189';

INSERT INTO `SERVICE_PRICES` (`service_id`,`hospital_id`,`price`,`currency`,`payer_type`,`area_tag`,`effective_from`,`effective_to`,`notes`,`status`)
SELECT `service_id`, 1, 6800000.00, 'VND', 'TU_CHI_TRA', NULL, '2024-01-01', NULL, NULL, 1
FROM `SERVICES`
WHERE `hospital_id` = 1 AND `code` = 'H190';

INSERT INTO `SERVICE_PRICES` (`service_id`,`hospital_id`,`price`,`currency`,`payer_type`,`area_tag`,`effective_from`,`effective_to`,`notes`,`status`)
SELECT `service_id`, 1, 975300.00, 'VND', 'BHYT', NULL, '2024-01-01', NULL, NULL, 1
FROM `SERVICES`
WHERE `hospital_id` = 1 AND `code` = 'H190';

INSERT INTO `SERVICE_PRICES` (`service_id`,`hospital_id`,`price`,`currency`,`payer_type`,`area_tag`,`effective_from`,`effective_to`,`notes`,`status`)
SELECT `service_id`, 1, 800000.00, 'VND', 'TU_CHI_TRA', NULL, '2024-01-01', NULL, NULL, 1
FROM `SERVICES`
WHERE `hospital_id` = 1 AND `code` = 'R105';

INSERT INTO `SERVICE_PRICES` (`service_id`,`hospital_id`,`price`,`currency`,`payer_type`,`area_tag`,`effective_from`,`effective_to`,`notes`,`status`)
SELECT `service_id`, 1, 218500.00, 'VND', 'BHYT', NULL, '2024-01-01', NULL, NULL, 1
FROM `SERVICES`
WHERE `hospital_id` = 1 AND `code` = 'R105';

INSERT INTO `SERVICE_PRICES` (`service_id`,`hospital_id`,`price`,`currency`,`payer_type`,`area_tag`,`effective_from`,`effective_to`,`notes`,`status`)
SELECT `service_id`, 1, 1200000.00, 'VND', 'TU_CHI_TRA', NULL, '2024-01-01', NULL, NULL, 1
FROM `SERVICES`
WHERE `hospital_id` = 1 AND `code` = 'R106';

INSERT INTO `SERVICE_PRICES` (`service_id`,`hospital_id`,`price`,`currency`,`payer_type`,`area_tag`,`effective_from`,`effective_to`,`notes`,`status`)
SELECT `service_id`, 1, 126700.00, 'VND', 'BHYT', NULL, '2024-01-01', NULL, NULL, 1
FROM `SERVICES`
WHERE `hospital_id` = 1 AND `code` = 'R106';

INSERT INTO `SERVICE_PRICES` (`service_id`,`hospital_id`,`price`,`currency`,`payer_type`,`area_tag`,`effective_from`,`effective_to`,`notes`,`status`)
SELECT `service_id`, 1, 2400000.00, 'VND', 'TU_CHI_TRA', NULL, '2024-01-01', NULL, NULL, 1
FROM `SERVICES`
WHERE `hospital_id` = 1 AND `code` = 'R113';

INSERT INTO `SERVICE_PRICES` (`service_id`,`hospital_id`,`price`,`currency`,`payer_type`,`area_tag`,`effective_from`,`effective_to`,`notes`,`status`)
SELECT `service_id`, 1, 414400.00, 'VND', 'BHYT', NULL, '2024-01-01', NULL, NULL, 1
FROM `SERVICES`
WHERE `hospital_id` = 1 AND `code` = 'R113';

INSERT INTO `SERVICE_PRICES` (`service_id`,`hospital_id`,`price`,`currency`,`payer_type`,`area_tag`,`effective_from`,`effective_to`,`notes`,`status`)
SELECT `service_id`, 1, 50000.00, 'VND', 'TU_CHI_TRA', NULL, '2024-01-01', NULL, NULL, 1
FROM `SERVICES`
WHERE `hospital_id` = 1 AND `code` = 'MF20';

INSERT INTO `SERVICE_PRICES` (`service_id`,`hospital_id`,`price`,`currency`,`payer_type`,`area_tag`,`effective_from`,`effective_to`,`notes`,`status`)
SELECT `service_id`, 1, 39900.00, 'VND', 'BHYT', NULL, '2024-01-01', NULL, NULL, 1
FROM `SERVICES`
WHERE `hospital_id` = 1 AND `code` = 'MF20';

INSERT INTO `SERVICE_PRICES` (`service_id`,`hospital_id`,`price`,`currency`,`payer_type`,`area_tag`,`effective_from`,`effective_to`,`notes`,`status`)
SELECT `service_id`, 1, 220000.00, 'VND', 'TU_CHI_TRA', NULL, '2024-01-01', NULL, NULL, 1
FROM `SERVICES`
WHERE `hospital_id` = 1 AND `code` = 'MF22';

INSERT INTO `SERVICE_PRICES` (`service_id`,`hospital_id`,`price`,`currency`,`payer_type`,`area_tag`,`effective_from`,`effective_to`,`notes`,`status`)
SELECT `service_id`, 1, 220000.00, 'VND', 'BHYT', NULL, '2024-01-01', NULL, NULL, 1
FROM `SERVICES`
WHERE `hospital_id` = 1 AND `code` = 'MF22';

INSERT INTO `SERVICE_PRICES` (`service_id`,`hospital_id`,`price`,`currency`,`payer_type`,`area_tag`,`effective_from`,`effective_to`,`notes`,`status`)
SELECT `service_id`, 1, 300000.00, 'VND', 'TU_CHI_TRA', NULL, '2024-01-01', NULL, NULL, 1
FROM `SERVICES`
WHERE `hospital_id` = 1 AND `code` = 'MF23';

INSERT INTO `SERVICE_PRICES` (`service_id`,`hospital_id`,`price`,`currency`,`payer_type`,`area_tag`,`effective_from`,`effective_to`,`notes`,`status`)
SELECT `service_id`, 1, 144300.00, 'VND', 'BHYT', NULL, '2024-01-01', NULL, NULL, 1
FROM `SERVICES`
WHERE `hospital_id` = 1 AND `code` = 'MF23';

INSERT INTO `SERVICE_PRICES` (`service_id`,`hospital_id`,`price`,`currency`,`payer_type`,`area_tag`,`effective_from`,`effective_to`,`notes`,`status`)
SELECT `service_id`, 1, 530000.00, 'VND', 'TU_CHI_TRA', NULL, '2024-01-01', NULL, NULL, 1
FROM `SERVICES`
WHERE `hospital_id` = 1 AND `code` = 'NZN1';

INSERT INTO `SERVICE_PRICES` (`service_id`,`hospital_id`,`price`,`currency`,`payer_type`,`area_tag`,`effective_from`,`effective_to`,`notes`,`status`)
SELECT `service_id`, 1, 325200.00, 'VND', 'BHYT', NULL, '2024-01-01', NULL, NULL, 1
FROM `SERVICES`
WHERE `hospital_id` = 1 AND `code` = 'NZN1';

INSERT INTO `SERVICE_PRICES` (`service_id`,`hospital_id`,`price`,`currency`,`payer_type`,`area_tag`,`effective_from`,`effective_to`,`notes`,`status`)
SELECT `service_id`, 1, 250000.00, 'VND', 'TU_CHI_TRA', NULL, '2024-01-01', NULL, NULL, 1
FROM `SERVICES`
WHERE `hospital_id` = 1 AND `code` = 'NZP2';

INSERT INTO `SERVICE_PRICES` (`service_id`,`hospital_id`,`price`,`currency`,`payer_type`,`area_tag`,`effective_from`,`effective_to`,`notes`,`status`)
SELECT `service_id`, 1, 250000.00, 'VND', 'BHYT', NULL, '2024-01-01', NULL, NULL, 1
FROM `SERVICES`
WHERE `hospital_id` = 1 AND `code` = 'NZP2';

INSERT INTO `SERVICE_PRICES` (`service_id`,`hospital_id`,`price`,`currency`,`payer_type`,`area_tag`,`effective_from`,`effective_to`,`notes`,`status`)
SELECT `service_id`, 1, 100000.00, 'VND', 'TU_CHI_TRA', NULL, '2024-01-01', NULL, NULL, 1
FROM `SERVICES`
WHERE `hospital_id` = 1 AND `code` = 'NZp3';

INSERT INTO `SERVICE_PRICES` (`service_id`,`hospital_id`,`price`,`currency`,`payer_type`,`area_tag`,`effective_from`,`effective_to`,`notes`,`status`)
SELECT `service_id`, 1, 45500.00, 'VND', 'BHYT', NULL, '2024-01-01', NULL, NULL, 1
FROM `SERVICES`
WHERE `hospital_id` = 1 AND `code` = 'NZp3';

INSERT INTO `SERVICE_PRICES` (`service_id`,`hospital_id`,`price`,`currency`,`payer_type`,`area_tag`,`effective_from`,`effective_to`,`notes`,`status`)
SELECT `service_id`, 1, 1578000.00, 'VND', 'TU_CHI_TRA', NULL, '2024-01-01', NULL, NULL, 1
FROM `SERVICES`
WHERE `hospital_id` = 1 AND `code` = 'MQ15';

INSERT INTO `SERVICE_PRICES` (`service_id`,`hospital_id`,`price`,`currency`,`payer_type`,`area_tag`,`effective_from`,`effective_to`,`notes`,`status`)
SELECT `service_id`, 1, 1578000.00, 'VND', 'BHYT', NULL, '2024-01-01', NULL, NULL, 1
FROM `SERVICES`
WHERE `hospital_id` = 1 AND `code` = 'MQ15';

INSERT INTO `SERVICE_PRICES` (`service_id`,`hospital_id`,`price`,`currency`,`payer_type`,`area_tag`,`effective_from`,`effective_to`,`notes`,`status`)
SELECT `service_id`, 1, 509000.00, 'VND', 'TU_CHI_TRA', NULL, '2024-01-01', NULL, NULL, 1
FROM `SERVICES`
WHERE `hospital_id` = 1 AND `code` = 'MQ16';

INSERT INTO `SERVICE_PRICES` (`service_id`,`hospital_id`,`price`,`currency`,`payer_type`,`area_tag`,`effective_from`,`effective_to`,`notes`,`status`)
SELECT `service_id`, 1, 391500.00, 'VND', 'BHYT', NULL, '2024-01-01', NULL, NULL, 1
FROM `SERVICES`
WHERE `hospital_id` = 1 AND `code` = 'MQ16';

INSERT INTO `SERVICE_PRICES` (`service_id`,`hospital_id`,`price`,`currency`,`payer_type`,`area_tag`,`effective_from`,`effective_to`,`notes`,`status`)
SELECT `service_id`, 1, 693000.00, 'VND', 'TU_CHI_TRA', NULL, '2024-01-01', NULL, NULL, 1
FROM `SERVICES`
WHERE `hospital_id` = 1 AND `code` = 'TPO5';

INSERT INTO `SERVICE_PRICES` (`service_id`,`hospital_id`,`price`,`currency`,`payer_type`,`area_tag`,`effective_from`,`effective_to`,`notes`,`status`)
SELECT `service_id`, 1, 510400.00, 'VND', 'BHYT', NULL, '2024-01-01', NULL, NULL, 1
FROM `SERVICES`
WHERE `hospital_id` = 1 AND `code` = 'TPO5';

INSERT INTO `SERVICE_PRICES` (`service_id`,`hospital_id`,`price`,`currency`,`payer_type`,`area_tag`,`effective_from`,`effective_to`,`notes`,`status`)
SELECT `service_id`, 1, 1984000.00, 'VND', 'TU_CHI_TRA', NULL, '2024-01-01', NULL, NULL, 1
FROM `SERVICES`
WHERE `hospital_id` = 1 AND `code` = 'TPP1';

INSERT INTO `SERVICE_PRICES` (`service_id`,`hospital_id`,`price`,`currency`,`payer_type`,`area_tag`,`effective_from`,`effective_to`,`notes`,`status`)
SELECT `service_id`, 1, 510400.00, 'VND', 'BHYT', NULL, '2024-01-01', NULL, NULL, 1
FROM `SERVICES`
WHERE `hospital_id` = 1 AND `code` = 'TPP1';

INSERT INTO `SERVICE_PRICES` (`service_id`,`hospital_id`,`price`,`currency`,`payer_type`,`area_tag`,`effective_from`,`effective_to`,`notes`,`status`)
SELECT `service_id`, 1, 3000000.00, 'VND', 'TU_CHI_TRA', NULL, '2024-01-01', NULL, NULL, 1
FROM `SERVICES`
WHERE `hospital_id` = 1 AND `code` = 'I121';

INSERT INTO `SERVICE_PRICES` (`service_id`,`hospital_id`,`price`,`currency`,`payer_type`,`area_tag`,`effective_from`,`effective_to`,`notes`,`status`)
SELECT `service_id`, 1, 162900.00, 'VND', 'BHYT', NULL, '2024-01-01', NULL, NULL, 1
FROM `SERVICES`
WHERE `hospital_id` = 1 AND `code` = 'I121';

INSERT INTO `SERVICE_PRICES` (`service_id`,`hospital_id`,`price`,`currency`,`payer_type`,`area_tag`,`effective_from`,`effective_to`,`notes`,`status`)
SELECT `service_id`, 1, 4300000.00, 'VND', 'TU_CHI_TRA', NULL, '2024-01-01', NULL, NULL, 1
FROM `SERVICES`
WHERE `hospital_id` = 1 AND `code` = 'I122';

INSERT INTO `SERVICE_PRICES` (`service_id`,`hospital_id`,`price`,`currency`,`payer_type`,`area_tag`,`effective_from`,`effective_to`,`notes`,`status`)
SELECT `service_id`, 1, 248500.00, 'VND', 'BHYT', NULL, '2024-01-01', NULL, NULL, 1
FROM `SERVICES`
WHERE `hospital_id` = 1 AND `code` = 'I122';

COMMIT;
