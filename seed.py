"""
Seed script for CầuLong.com
Run: python seed.py
Also importable: from seed import seed_all; seed_all()
"""
from app.extensions import db
from app.models import User, Brand, Racket, RacketImage, BlogPost, Review, Tag, generate_slug


def seed_all():
    """Idempotent seed — safe to call multiple times."""
    db.create_all()

    # ── Admin User ──────────────────────────────────────────────────────
    admin = User.query.filter_by(username='admin').first()
    if not admin:
        admin = User(username='admin', email='admin@caulong.com', is_admin=True)
        db.session.add(admin)
        print('Created admin user.')
    else:
        print('Admin user already exists — resetting password.')
    admin.set_password('admin123')
    admin.is_admin = True
    db.session.flush()

    # ── Brands ──────────────────────────────────────────────────────────
    brands_data = [
        {
            'name': 'Yonex',
            'country': 'Nhật Bản',
            'description': 'Yonex là thương hiệu vợt cầu lông hàng đầu thế giới của Nhật Bản, được thành lập từ năm 1946. Với công nghệ tiên tiến như Aero Frame, Isometric và Nanometric, Yonex luôn là lựa chọn hàng đầu của các vận động viên chuyên nghiệp từ khắp nơi trên thế giới.',
        },
        {
            'name': 'Victor',
            'country': 'Đài Loan',
            'description': 'Victor là thương hiệu cầu lông đến từ Đài Loan, được thành lập năm 1968. Nổi tiếng với dòng vợt Thruster và DriveX, Victor cung cấp các sản phẩm chất lượng cao với công nghệ tiên tiến, phù hợp cho cả người chơi nghiệp dư lẫn chuyên nghiệp.',
        },
        {
            'name': 'Li-Ning',
            'country': 'Trung Quốc',
            'description': 'Li-Ning là thương hiệu thể thao của Trung Quốc, được thành lập bởi nhà thể dục dụng cụ huyền thoại Li Ning vào năm 1989. Dòng vợt N9 và Turbocharging nổi tiếng về sự kết hợp giữa sức mạnh và kiểm soát vượt trội.',
        },
        {
            'name': 'Mizuno',
            'country': 'Nhật Bản',
            'description': 'Mizuno là tập đoàn thể thao lâu đời của Nhật Bản, được thành lập từ năm 1906. Vợt cầu lông Mizuno nổi tiếng với chất lượng cao cấp, thiết kế tinh tế và công nghệ vật liệu tiên tiến, đặc biệt phù hợp với người chơi trình độ cao.',
        },
        {
            'name': 'Apacs',
            'country': 'Malaysia',
            'description': 'Apacs là thương hiệu cầu lông nổi tiếng từ Malaysia, được thành lập năm 2005. Apacs cung cấp các dòng vợt chất lượng cao với giá cả hợp lý, được nhiều người chơi tại Đông Nam Á ưa chuộng.',
        },
    ]

    brands = {}
    for bd in brands_data:
        slug = generate_slug(bd['name'])
        b = Brand.query.filter_by(slug=slug).first()
        if not b:
            b = Brand(
                name=bd['name'],
                slug=slug,
                country=bd['country'],
                description=bd['description'],
            )
            db.session.add(b)
            db.session.flush()
            print(f'Created brand: {bd["name"]}')
        brands[bd['name']] = b

    # ── Tags ────────────────────────────────────────────────────────────
    tags_data = ['Tấn công', 'Phòng thủ', 'Phong trào', 'Tốc độ', 'Sức mạnh', 'Kiểm soát', 'Chuyên nghiệp']
    tags = {}
    for t in tags_data:
        slug = generate_slug(t)
        tag = Tag.query.filter_by(slug=slug).first()
        if not tag:
            tag = Tag(name=t, slug=slug)
            db.session.add(tag)
            db.session.flush()
        tags[t] = tag

    # ── Rackets ─────────────────────────────────────────────────────────
    rackets_data = [
        # Yonex rackets
        {
            'name': 'Yonex Astrox 88D Pro',
            'brand': 'Yonex',
            'weight_class': '4U',
            'balance_type': 'head_heavy',
            'flexibility': 'stiff',
            'frame_material': 'HM Graphite, Nanometric DR',
            'shaft_material': 'HM Graphite, Nanometric',
            'skill_level': 'advanced',
            'price': 4500000,
            'string_tension_min': 20,
            'string_tension_max': 29,
            'length_mm': 675,
            'is_featured': True,
            'description': '<p>Yonex Astrox 88D Pro là phiên bản nâng cấp của dòng Astrox 88D được thiết kế đặc biệt cho người chơi đôi. Cây vợt này sử dụng công nghệ Rotational Generator System cho phép tạo ra những cú đập mạnh mẽ từ khu vực đuôi.</p><p>Với cân bằng nặng đầu và cán cứng, Astrox 88D Pro là vũ khí lý tưởng cho những pha đập cầu quyết định và tấn công từ phía sau sân.</p>',
            'pros': '- Sức mạnh đập cầu vượt trội\n- Khung siêu bền với công nghệ Nanometric DR\n- Độ chính xác cao khi tấn công\n- Màu sắc đẹp, thiết kế chuyên nghiệp',
            'cons': '- Giá thành cao\n- Không phù hợp với người mới\n- Đòi hỏi kỹ thuật tốt để phát huy tối đa',
            'playing_style': 'Phù hợp nhất cho người chơi cầu lông đôi ở vị trí đánh phía sau, những người thích lối chơi tấn công với các pha smash mạnh mẽ và quyết định. Cũng phù hợp cho người đơn muốn kiểm soát tốc độ cuộc chơi.',
            'tags': ['Tấn công', 'Sức mạnh', 'Chuyên nghiệp'],
        },
        {
            'name': 'Yonex Astrox 99 Pro',
            'brand': 'Yonex',
            'weight_class': '4U',
            'balance_type': 'head_heavy',
            'flexibility': 'stiff',
            'frame_material': 'HM Graphite, Nanometric DR, Tungsten',
            'shaft_material': 'HM Graphite, Nanometric',
            'skill_level': 'professional',
            'price': 5800000,
            'string_tension_min': 20,
            'string_tension_max': 30,
            'length_mm': 675,
            'is_featured': True,
            'description': '<p>Yonex Astrox 99 Pro là đỉnh cao của dòng vợt Astrox, được sử dụng bởi nhà vô địch thế giới Kento Momota. Sử dụng công nghệ mới nhất bao gồm Tungsten Infused Grommets để tối ưu hóa căng dây và tăng cường tiếp xúc cầu.</p>',
            'pros': '- Công nghệ đỉnh cao nhất của Yonex\n- Sức mạnh smash cực kỳ mạnh mẽ\n- Độ bền khung vượt trội\n- Được sử dụng bởi VĐV chuyên nghiệp hàng đầu',
            'cons': '- Giá rất cao\n- Chỉ phù hợp với người chơi có kinh nghiệm\n- Khó kiểm soát ở tốc độ nhanh',
            'playing_style': 'Dành cho người chơi chuyên nghiệp hoặc nâng cao với phong cách tấn công mạnh mẽ, tập trung vào smash và tấn công quyết đoán từ phía sau sân.',
            'tags': ['Tấn công', 'Sức mạnh', 'Chuyên nghiệp'],
        },
        {
            'name': 'Yonex Nanoflare 1000Z',
            'brand': 'Yonex',
            'weight_class': '4U',
            'balance_type': 'head_light',
            'flexibility': 'extra_stiff',
            'frame_material': 'Torayca M40X, Nanometric',
            'shaft_material': 'Torayca M40X',
            'skill_level': 'professional',
            'price': 6200000,
            'string_tension_min': 20,
            'string_tension_max': 30,
            'length_mm': 675,
            'is_featured': True,
            'description': '<p>Yonex Nanoflare 1000Z là vợt tốc độ đỉnh cao, được thiết kế để đạt tốc độ vung vợt tối đa. Sử dụng sợi carbon Torayca M40X cao cấp và khung Diamond Frame mới, vợt mang lại khả năng kiểm soát và tốc độ chưa từng có.</p>',
            'pros': '- Tốc độ vung vợt cực kỳ nhanh\n- Nhẹ đầu cho phép phòng thủ tốt\n- Thiết kế khung độc đáo Diamond Frame\n- Kiểm soát xuất sắc',
            'cons': '- Giá rất cao\n- Sức mạnh smash kém hơn dòng Astrox\n- Đòi hỏi kỹ thuật cao',
            'playing_style': 'Phù hợp cho người chơi tốc độ, thích lối chơi linh hoạt với nhiều cú tấn công nhanh, đặc biệt ở đơn nam và đôi nam.',
            'tags': ['Tốc độ', 'Chuyên nghiệp'],
        },
        {
            'name': 'Yonex Arcsaber 11 Pro',
            'brand': 'Yonex',
            'weight_class': '4U',
            'balance_type': 'even',
            'flexibility': 'medium',
            'frame_material': 'HM Graphite, Nanometric',
            'shaft_material': 'HM Graphite',
            'skill_level': 'advanced',
            'price': 4200000,
            'string_tension_min': 19,
            'string_tension_max': 29,
            'length_mm': 675,
            'is_featured': False,
            'description': '<p>Yonex Arcsaber 11 Pro là sự kết hợp hoàn hảo giữa sức mạnh và kiểm soát. Vợt cân bằng đầu cho phép người chơi phát triển toàn diện cả tấn công lẫn phòng thủ.</p>',
            'pros': '- Cân bằng hoàn hảo giữa sức mạnh và kiểm soát\n- Phù hợp đa dạng phong cách\n- Độ bền tốt\n- Cảm giác cầu xuất sắc',
            'cons': '- Không vượt trội ở bất kỳ khía cạnh nào\n- Giá hơi cao so với tầm trung',
            'playing_style': 'Phù hợp cho người chơi toàn diện, không thiên về tấn công hay phòng thủ. Đặc biệt tốt cho người đang nâng cấp kỹ thuật.',
            'tags': ['Kiểm soát'],
        },
        {
            'name': 'Yonex Duora 10',
            'brand': 'Yonex',
            'weight_class': '3U',
            'balance_type': 'even',
            'flexibility': 'stiff',
            'frame_material': 'HM Graphite, Super HMG',
            'shaft_material': 'HM Graphite',
            'skill_level': 'advanced',
            'price': 3800000,
            'string_tension_min': 20,
            'string_tension_max': 28,
            'length_mm': 675,
            'is_featured': False,
            'description': '<p>Yonex Duora 10 với thiết kế khung độc đáo hai mặt - một mặt tối ưu cho đánh cầu bằng cổ tay (forehand) và mặt kia cho backhand. Công nghệ Dual Optimum System cho phép tối ưu hóa từng cú đánh.</p>',
            'pros': '- Thiết kế độc đáo tối ưu cả forehand và backhand\n- Cảm giác cầu khác biệt\n- Phù hợp cho người chơi kỹ thuật',
            'cons': '- Cần thời gian làm quen\n- Nặng hơn các dòng thông thường\n- Giá cao',
            'playing_style': 'Phù hợp cho người chơi kỹ thuật tốt, thích phân tích và kiểm soát từng cú đánh, chú trọng kỹ thuật hơn sức mạnh.',
            'tags': ['Kiểm soát', 'Tấn công'],
        },
        # Victor rackets
        {
            'name': 'Victor Thruster K 9900',
            'brand': 'Victor',
            'weight_class': '4U',
            'balance_type': 'head_heavy',
            'flexibility': 'extra_stiff',
            'frame_material': 'High Resilience Modulus Graphite, Nano Fortify TR+',
            'shaft_material': 'Ultra High Resilience Modulus Graphite',
            'skill_level': 'professional',
            'price': 5500000,
            'string_tension_min': 20,
            'string_tension_max': 30,
            'length_mm': 675,
            'is_featured': True,
            'description': '<p>Victor Thruster K 9900 là vợt đỉnh cao của dòng Thruster, được thiết kế cho những cú smash vũ bão. Khung vợt sử dụng công nghệ Nano Fortify TR+ giúp tăng cường độ cứng và sức mạnh truyền lực.</p>',
            'pros': '- Sức mạnh smash vô song\n- Cán siêu cứng tối ưu lực truyền\n- Chất lượng vật liệu cao cấp\n- Được sử dụng bởi các VĐV hàng đầu',
            'cons': '- Rất khó cho người chơi mới\n- Giá thành cao\n- Phòng thủ và di chuyển hạn chế hơn',
            'playing_style': 'Dành riêng cho người chơi chuyên nghiệp với phong cách tấn công hung hăng, đặc biệt ở môn đơn. Cần có thể lực và kỹ thuật tốt để kiểm soát.',
            'tags': ['Tấn công', 'Sức mạnh', 'Chuyên nghiệp'],
        },
        {
            'name': 'Victor Jetspeed S 12 II',
            'brand': 'Victor',
            'weight_class': '4U',
            'balance_type': 'head_light',
            'flexibility': 'stiff',
            'frame_material': 'High Resilience Modulus Graphite, Nano Fortify TR',
            'shaft_material': 'Ultra High Resilience Modulus Graphite',
            'skill_level': 'advanced',
            'price': 4800000,
            'string_tension_min': 19,
            'string_tension_max': 30,
            'length_mm': 675,
            'is_featured': True,
            'description': '<p>Victor Jetspeed S 12 II được thiết kế để đạt tốc độ tối đa, phù hợp với lối chơi cầu lông hiện đại đòi hỏi sự nhanh nhạy và phản xạ tốt. Khung vợt aerodynamic giúp giảm lực cản không khí.</p>',
            'pros': '- Tốc độ vung vợt rất nhanh\n- Nhẹ đầu giúp phòng thủ linh hoạt\n- Khung aerodynamic giảm lực cản\n- Cảm giác cầu nhạy bén',
            'cons': '- Sức mạnh đập cầu vừa phải\n- Giá cao\n- Đòi hỏi người chơi có kinh nghiệm',
            'playing_style': 'Phù hợp cho người chơi tốc độ, thích tấn công nhanh và phòng thủ linh hoạt, đặc biệt phù hợp cho môn đôi nam và đơn nữ.',
            'tags': ['Tốc độ', 'Chuyên nghiệp'],
        },
        {
            'name': 'Victor DriveX 10 Meta',
            'brand': 'Victor',
            'weight_class': '4U',
            'balance_type': 'even',
            'flexibility': 'medium',
            'frame_material': 'High Resilience Modulus Graphite',
            'shaft_material': 'High Resilience Modulus Graphite',
            'skill_level': 'intermediate',
            'price': 2800000,
            'string_tension_min': 18,
            'string_tension_max': 27,
            'length_mm': 675,
            'is_featured': False,
            'description': '<p>Victor DriveX 10 Meta là vợt toàn diện phù hợp cho người chơi trung cấp muốn nâng cao kỹ năng. Thiết kế cân bằng giúp người chơi phát triển đều cả hai mặt tấn công và phòng thủ.</p>',
            'pros': '- Giá cả phải chăng\n- Phù hợp đa năng\n- Dễ làm quen\n- Chất lượng tốt trong tầm giá',
            'cons': '- Không xuất sắc ở bất kỳ điểm nào\n- Không phù hợp người chơi chuyên nghiệp',
            'playing_style': 'Phù hợp cho người chơi trung cấp muốn cải thiện kỹ thuật toàn diện, không thiên về phong cách cụ thể nào.',
            'tags': ['Kiểm soát', 'Phong trào'],
        },
        {
            'name': 'Victor Hypernano X 900',
            'brand': 'Victor',
            'weight_class': '4U',
            'balance_type': 'head_heavy',
            'flexibility': 'stiff',
            'frame_material': 'High Resilience Modulus Graphite, Hard Cored Technology',
            'shaft_material': 'High Resilience Modulus Graphite',
            'skill_level': 'advanced',
            'price': 3600000,
            'string_tension_min': 19,
            'string_tension_max': 29,
            'length_mm': 675,
            'is_featured': False,
            'description': '<p>Victor Hypernano X 900 kết hợp công nghệ Hard Cored Technology giúp khung vợt cứng hơn 5% so với trước trong khi vẫn giữ được trọng lượng nhẹ.</p>',
            'pros': '- Sức mạnh tốt\n- Công nghệ Hard Cored đột phá\n- Giá hợp lý cho chất lượng\n- Độ bền cao',
            'cons': '- Tốc độ hạn chế hơn dòng Jetspeed\n- Không phù hợp người mới',
            'playing_style': 'Phù hợp cho người chơi nâng cao thích lối chơi tấn công có kiểm soát.',
            'tags': ['Tấn công', 'Kiểm soát'],
        },
        # Li-Ning rackets
        {
            'name': 'Li-Ning Tectonic 9',
            'brand': 'Li-Ning',
            'weight_class': '4U',
            'balance_type': 'head_heavy',
            'flexibility': 'extra_stiff',
            'frame_material': 'TB Nano, W-Speed, TP-50',
            'shaft_material': 'TB Nano',
            'skill_level': 'professional',
            'price': 5200000,
            'string_tension_min': 20,
            'string_tension_max': 30,
            'length_mm': 675,
            'is_featured': True,
            'description': '<p>Li-Ning Tectonic 9 là vợt đỉnh cao của Li-Ning với công nghệ TB Nano và W-Speed frame, mang lại hiệu suất tuyệt vời cho các vận động viên chuyên nghiệp. Thiết kế được phát triển cùng với nhà vô địch thế giới Chen Long.</p>',
            'pros': '- Sức mạnh smash vượt trội\n- Công nghệ vật liệu tiên tiến\n- Thiết kế chuyên nghiệp\n- Được VĐV top thế giới sử dụng',
            'cons': '- Giá rất cao\n- Chỉ phù hợp người chơi cao cấp\n- Đòi hỏi kỹ thuật hoàn thiện',
            'playing_style': 'Dành cho người chơi chuyên nghiệp với phong cách tấn công mạnh mẽ, tập trung vào smash từ phía sau sân.',
            'tags': ['Tấn công', 'Sức mạnh', 'Chuyên nghiệp'],
        },
        {
            'name': 'Li-Ning Windstorm 500',
            'brand': 'Li-Ning',
            'weight_class': '5U',
            'balance_type': 'head_light',
            'flexibility': 'medium',
            'frame_material': 'High Modulus Graphite',
            'shaft_material': 'High Modulus Graphite',
            'skill_level': 'intermediate',
            'price': 1800000,
            'string_tension_min': 18,
            'string_tension_max': 26,
            'length_mm': 675,
            'is_featured': False,
            'description': '<p>Li-Ning Windstorm 500 là lựa chọn tốt cho người chơi trung cấp muốn cải thiện tốc độ và sự linh hoạt. Vợt siêu nhẹ 5U giúp người chơi phản xạ nhanh hơn.</p>',
            'pros': '- Cực kỳ nhẹ và nhanh\n- Giá phải chăng\n- Phù hợp luyện tập hàng ngày\n- Tốt cho người mới lên trung cấp',
            'cons': '- Sức mạnh hạn chế\n- Độ bền không cao bằng dòng cao cấp',
            'playing_style': 'Phù hợp người chơi phong trào và trung cấp, thích lối chơi nhanh và linh hoạt.',
            'tags': ['Tốc độ', 'Phong trào'],
        },
        {
            'name': 'Li-Ning N9 II',
            'brand': 'Li-Ning',
            'weight_class': '4U',
            'balance_type': 'head_heavy',
            'flexibility': 'stiff',
            'frame_material': 'TB Nano, OC Technology',
            'shaft_material': 'TB Nano',
            'skill_level': 'advanced',
            'price': 3200000,
            'string_tension_min': 19,
            'string_tension_max': 28,
            'length_mm': 675,
            'is_featured': False,
            'description': '<p>Li-Ning N9 II là phiên bản kế thừa của dòng N9 huyền thoại, được cải tiến với công nghệ OC Technology mới nhất. Vợt mang đến sức mạnh vượt trội trong khi vẫn giữ được cảm giác cầu nhạy bén.</p>',
            'pros': '- Sức mạnh tốt trong tầm giá\n- Công nghệ OC độc quyền\n- Cảm giác cầu tốt\n- Thiết kế đẹp mắt',
            'cons': '- Không phù hợp người mới\n- Đòi hỏi kỹ thuật nhất định',
            'playing_style': 'Phù hợp người chơi nâng cao muốn tấn công mạnh với khả năng kiểm soát tốt.',
            'tags': ['Tấn công', 'Sức mạnh'],
        },
        # Mizuno rackets
        {
            'name': 'Mizuno Altius 01',
            'brand': 'Mizuno',
            'weight_class': '4U',
            'balance_type': 'head_heavy',
            'flexibility': 'stiff',
            'frame_material': 'DiamondCore Technology, Graphite',
            'shaft_material': 'Graphite',
            'skill_level': 'professional',
            'price': 4900000,
            'string_tension_min': 20,
            'string_tension_max': 30,
            'length_mm': 675,
            'is_featured': False,
            'description': '<p>Mizuno Altius 01 là vợt flagship của Mizuno, được phát triển với công nghệ DiamondCore Technology độc quyền. Vợt mang lại sức mạnh smash vượt trội và độ bền đặc biệt cao.</p>',
            'pros': '- Chất lượng Nhật Bản hàng đầu\n- Công nghệ DiamondCore độc quyền\n- Độ bền cực cao\n- Cảm giác cao cấp khi đánh',
            'cons': '- Giá thành rất cao\n- Tốc độ không bằng dòng nhẹ đầu\n- Khó tìm mua tại Việt Nam',
            'playing_style': 'Phù hợp người chơi chuyên nghiệp và nâng cao, đặc biệt phù hợp cho các pha smash quyết định và lối chơi tấn công.',
            'tags': ['Tấn công', 'Chuyên nghiệp'],
        },
        {
            'name': 'Mizuno Altius 05 Feel',
            'brand': 'Mizuno',
            'weight_class': '5U',
            'balance_type': 'even',
            'flexibility': 'flexible',
            'frame_material': 'Graphite',
            'shaft_material': 'Graphite',
            'skill_level': 'beginner',
            'price': 1500000,
            'string_tension_min': 17,
            'string_tension_max': 25,
            'length_mm': 675,
            'is_featured': False,
            'description': '<p>Mizuno Altius 05 Feel được thiết kế dành riêng cho người mới bắt đầu chơi cầu lông. Cán mềm và cân bằng đều giúp người chơi dễ dàng làm quen với kỹ thuật cơ bản.</p>',
            'pros': '- Dễ sử dụng cho người mới\n- Giá cả phải chăng\n- Chất lượng Mizuno đáng tin cậy\n- Nhẹ và dễ điều khiển',
            'cons': '- Không phù hợp người chơi có kinh nghiệm\n- Cán mềm hạn chế sức mạnh',
            'playing_style': 'Lý tưởng cho người mới bắt đầu học cầu lông, muốn nắm vững kỹ thuật cơ bản trước khi nâng cấp.',
            'tags': ['Phong trào'],
        },
        # Apacs rackets
        {
            'name': 'Apacs Lethal 10',
            'brand': 'Apacs',
            'weight_class': '4U',
            'balance_type': 'head_heavy',
            'flexibility': 'stiff',
            'frame_material': 'High Modulus Graphite',
            'shaft_material': 'High Modulus Graphite',
            'skill_level': 'advanced',
            'price': 2500000,
            'string_tension_min': 20,
            'string_tension_max': 30,
            'length_mm': 680,
            'is_featured': False,
            'description': '<p>Apacs Lethal 10 là vợt tấn công cao cấp của Apacs, nổi tiếng với sức mạnh smash đáng gờm. Với chiều dài 680mm, vợt cung cấp góc đánh rộng hơn so với tiêu chuẩn.</p>',
            'pros': '- Sức mạnh smash tốt\n- Chiều dài 680mm cho góc đánh rộng hơn\n- Giá cả hợp lý\n- Chất lượng tốt trong phân khúc',
            'cons': '- Thương hiệu ít nổi tiếng hơn\n- Khó tìm phụ kiện thay thế',
            'playing_style': 'Phù hợp người chơi nâng cao muốn sức mạnh smash tốt với chi phí thấp hơn các thương hiệu lớn.',
            'tags': ['Tấn công', 'Sức mạnh'],
        },
        {
            'name': 'Apacs Z-Ziggler Pro',
            'brand': 'Apacs',
            'weight_class': '5U',
            'balance_type': 'head_light',
            'flexibility': 'medium',
            'frame_material': 'High Modulus Graphite',
            'shaft_material': 'High Modulus Graphite',
            'skill_level': 'beginner',
            'price': 950000,
            'string_tension_min': 17,
            'string_tension_max': 24,
            'length_mm': 675,
            'is_featured': False,
            'description': '<p>Apacs Z-Ziggler Pro là vợt phổ thông dành cho người mới với giá cả rất phải chăng. Đây là lựa chọn tốt cho những ai muốn bắt đầu hành trình cầu lông mà không cần đầu tư quá nhiều.</p>',
            'pros': '- Giá rất rẻ\n- Nhẹ và dễ sử dụng\n- Phù hợp tập luyện hàng ngày\n- Tốt cho người mới bắt đầu',
            'cons': '- Chất lượng hạn chế\n- Không bền bằng dòng cao cấp\n- Không phù hợp người chơi có kinh nghiệm',
            'playing_style': 'Phù hợp hoàn toàn cho người mới bắt đầu và chơi phong trào, không cần đầu tư nhiều.',
            'tags': ['Phong trào'],
        },
        {
            'name': 'Apacs Nano Fusion Speed 722',
            'brand': 'Apacs',
            'weight_class': '5U',
            'balance_type': 'head_light',
            'flexibility': 'stiff',
            'frame_material': 'Hi-Modulus Graphite, Nano Technology',
            'shaft_material': 'Hi-Modulus Graphite',
            'skill_level': 'intermediate',
            'price': 1700000,
            'string_tension_min': 18,
            'string_tension_max': 28,
            'length_mm': 675,
            'is_featured': False,
            'description': '<p>Apacs Nano Fusion Speed 722 kết hợp công nghệ Nano Technology với thiết kế nhẹ 5U, mang lại tốc độ vung vợt nhanh ở mức giá hợp lý.</p>',
            'pros': '- Giá tốt cho chất lượng\n- Tốc độ vung vợt nhanh\n- Công nghệ Nano\n- Nhẹ và cơ động',
            'cons': '- Sức mạnh hạn chế\n- Không phù hợp tấn công mạnh',
            'playing_style': 'Phù hợp người chơi trung cấp thích tốc độ và sự linh hoạt với ngân sách hợp lý.',
            'tags': ['Tốc độ', 'Phong trào'],
        },
        {
            'name': 'Yonex Voltric 80 E-tune',
            'brand': 'Yonex',
            'weight_class': '3U',
            'balance_type': 'head_heavy',
            'flexibility': 'stiff',
            'frame_material': 'HM Graphite, Tungsten',
            'shaft_material': 'HM Graphite',
            'skill_level': 'intermediate',
            'price': 2900000,
            'string_tension_min': 19,
            'string_tension_max': 28,
            'length_mm': 675,
            'is_featured': False,
            'description': '<p>Yonex Voltric 80 E-tune là vợt đánh cầu nặng đầu phù hợp cho người chơi trung cấp muốn cải thiện sức mạnh smash. Với công nghệ Nanometric và Tungsten, vợt mang lại trọng tâm tối ưu.</p>',
            'pros': '- Sức mạnh tốt cho trung cấp\n- Thương hiệu Yonex uy tín\n- Giá hợp lý\n- Phù hợp nâng cao kỹ năng smash',
            'cons': '- Nặng hơn 3U so với 4U\n- Tốc độ hạn chế',
            'playing_style': 'Phù hợp người chơi trung cấp muốn tập trung phát triển kỹ năng tấn công và smash.',
            'tags': ['Tấn công', 'Sức mạnh'],
        },
        {
            'name': 'Victor Thruster F Claw',
            'brand': 'Victor',
            'weight_class': '4U',
            'balance_type': 'head_heavy',
            'flexibility': 'stiff',
            'frame_material': 'High Resilience Modulus Graphite',
            'shaft_material': 'Ultra High Resilience Modulus Graphite',
            'skill_level': 'intermediate',
            'price': 2200000,
            'string_tension_min': 18,
            'string_tension_max': 27,
            'length_mm': 675,
            'is_featured': False,
            'description': '<p>Victor Thruster F Claw là phiên bản phổ thông hơn của dòng Thruster, mang lại sức mạnh tốt cho người chơi trung cấp với mức giá hợp lý.</p>',
            'pros': '- Giá phải chăng\n- Sức mạnh tốt\n- Thương hiệu Victor uy tín\n- Phù hợp nâng cao kỹ năng',
            'cons': '- Không bằng dòng cao cấp Thruster K\n- Hạn chế ở tốc độ',
            'playing_style': 'Phù hợp người chơi trung cấp muốn cải thiện sức mạnh tấn công với ngân sách vừa phải.',
            'tags': ['Tấn công'],
        },
    ]

    for rd in rackets_data:
        slug = generate_slug(rd['name'])
        r = Racket.query.filter_by(slug=slug).first()
        if not r:
            brand = brands.get(rd['brand'])
            if not brand:
                continue
            r = Racket(
                name=rd['name'],
                slug=slug,
                brand_id=brand.id,
                weight_class=rd.get('weight_class'),
                balance_type=rd.get('balance_type'),
                flexibility=rd.get('flexibility'),
                frame_material=rd.get('frame_material'),
                shaft_material=rd.get('shaft_material'),
                skill_level=rd.get('skill_level'),
                price=rd.get('price'),
                description=rd.get('description'),
                pros=rd.get('pros'),
                cons=rd.get('cons'),
                playing_style=rd.get('playing_style'),
                string_tension_min=rd.get('string_tension_min'),
                string_tension_max=rd.get('string_tension_max'),
                length_mm=rd.get('length_mm', 675),
                is_featured=rd.get('is_featured', False),
                meta_title=rd['name'] + ' - ' + rd['brand'] + ' | CầuLong.com',
                meta_description='Đánh giá chi tiết ' + rd['name'] + ' của ' + rd['brand'] + '. Xem thông số kỹ thuật, ưu nhược điểm và giá bán tại CầuLong.com.',
            )
            for tag_name in rd.get('tags', []):
                tag = tags.get(tag_name)
                if tag:
                    r.tags.append(tag)
            db.session.add(r)
            db.session.flush()
            print(f'Created racket: {rd["name"]}')

    # ── Blog Posts ──────────────────────────────────────────────────────
    posts_data = [
        {
            'title': 'Hướng Dẫn Chọn Vợt Cầu Lông Cho Người Mới Bắt Đầu',
            'content': '''<h2>Tại Sao Việc Chọn Vợt Quan Trọng?</h2>
<p>Chiếc vợt cầu lông phù hợp có thể tạo ra sự khác biệt lớn trong quá trình học tập và phát triển kỹ năng. Một cây vợt không phù hợp không chỉ ảnh hưởng đến hiệu suất mà còn có thể gây chấn thương không mong muốn.</p>

<h2>Các Tiêu Chí Cần Xem Xét</h2>

<h3>1. Trọng Lượng (Weight Class)</h3>
<p>Vợt cầu lông thường được phân loại theo trọng lượng:</p>
<ul>
<li><strong>3U (85-89g)</strong>: Nặng nhất, phù hợp cho người thích smash mạnh</li>
<li><strong>4U (80-84g)</strong>: Phổ biến nhất, cân bằng giữa sức mạnh và tốc độ</li>
<li><strong>5U (75-79g)</strong>: Nhẹ nhất, phù hợp cho người thích tốc độ</li>
</ul>
<p>Người mới nên bắt đầu với vợt 4U hoặc 5U để dễ điều khiển hơn.</p>

<h3>2. Cân Bằng (Balance)</h3>
<ul>
<li><strong>Nặng đầu (Head Heavy)</strong>: Tạo sức mạnh smash tốt, phù hợp lối chơi tấn công</li>
<li><strong>Nhẹ đầu (Head Light)</strong>: Phản xạ nhanh, phù hợp phòng thủ</li>
<li><strong>Cân bằng (Even)</strong>: Toàn diện, phù hợp người mới</li>
</ul>

<h3>3. Độ Cứng Cán</h3>
<p>Cán cứng phù hợp với người có kỹ thuật tốt và muốn kiểm soát. Cán mềm thì phù hợp người mới vì dễ tạo lực hơn.</p>

<h2>Lời Khuyên Cho Người Mới</h2>
<p>Nếu bạn mới bắt đầu, hãy chọn một cây vợt trong tầm giá từ 500,000 - 1,500,000 VNĐ với đặc điểm:</p>
<ul>
<li>Trọng lượng 4U hoặc 5U</li>
<li>Cân bằng đều hoặc nhẹ đầu</li>
<li>Cán từ trung bình đến mềm</li>
</ul>
<p>Đừng đầu tư quá nhiều vào vợt khi mới bắt đầu - hãy tập trung vào kỹ thuật cơ bản trước!</p>''',
            'meta_title': 'Hướng Dẫn Chọn Vợt Cầu Lông Cho Người Mới | CầuLong.com',
            'meta_description': 'Tìm hiểu cách chọn vợt cầu lông phù hợp khi mới bắt đầu. Hướng dẫn chi tiết về trọng lượng, cân bằng và độ cứng cán.',
            'is_published': True,
        },
        {
            'title': 'So Sánh Yonex vs Victor: Thương Hiệu Nào Tốt Hơn?',
            'content': '''<h2>Tổng Quan</h2>
<p>Yonex và Victor là hai thương hiệu cầu lông hàng đầu thế giới, mỗi hãng có những ưu điểm riêng biệt. Bài viết này sẽ giúp bạn hiểu rõ hơn về sự khác biệt giữa hai thương hiệu để đưa ra lựa chọn phù hợp.</p>

<h2>Yonex - Truyền Thống Nhật Bản</h2>
<p>Yonex, thành lập năm 1946 tại Nhật Bản, là thương hiệu được hầu hết các vận động viên cầu lông hàng đầu thế giới tin dùng. Các công nghệ nổi bật:</p>
<ul>
<li><strong>Nanometric</strong>: Sợi carbon siêu mỏng tăng độ bền</li>
<li><strong>Isometric Frame</strong>: Khung vuông tăng diện tích ngọt</li>
<li><strong>Aero Frame</strong>: Khung aerodynamic giảm lực cản</li>
</ul>

<h2>Victor - Sáng Tạo Từ Đài Loan</h2>
<p>Victor, thành lập năm 1968 tại Đài Loan, nổi tiếng với sự đổi mới công nghệ và giá cả cạnh tranh:</p>
<ul>
<li><strong>Nano Fortify TR</strong>: Tăng cường độ cứng khung</li>
<li><strong>Rebound Shield</strong>: Hệ thống phản lực cải tiến</li>
<li><strong>TF Technology</strong>: Công nghệ tần số dao động khung</li>
</ul>

<h2>So Sánh Trực Tiếp</h2>
<table>
<tr><th>Tiêu Chí</th><th>Yonex</th><th>Victor</th></tr>
<tr><td>Giá</td><td>Cao hơn</td><td>Hợp lý hơn</td></tr>
<tr><td>Độ bền</td><td>Rất tốt</td><td>Tốt</td></tr>
<tr><td>Phân khúc</td><td>Rộng</td><td>Rộng</td></tr>
<tr><td>VĐV nổi tiếng</td><td>Kento Momota</td><td>Kevin Sanjaya</td></tr>
</table>

<h2>Kết Luận</h2>
<p>Cả hai thương hiệu đều xuất sắc. Nếu ngân sách là ưu tiên, Victor có nhiều lựa chọn tốt ở tầm giá thấp hơn. Nếu bạn muốn vợt được nhiều VĐV thế giới sử dụng nhất, Yonex là lựa chọn an toàn.</p>''',
            'meta_title': 'Yonex vs Victor: Thương Hiệu Nào Tốt Hơn 2024? | CầuLong.com',
            'meta_description': 'So sánh chi tiết Yonex và Victor - hai thương hiệu vợt cầu lông hàng đầu thế giới. Tìm hiểu ưu nhược điểm của từng hãng.',
            'is_published': True,
        },
        {
            'title': 'Lực Căng Dây Cầu Lông: Bao Nhiêu Là Phù Hợp?',
            'content': '''<h2>Tầm Quan Trọng Của Lực Căng Dây</h2>
<p>Lực căng dây (string tension) ảnh hưởng trực tiếp đến cảm giác đánh, sức mạnh và kiểm soát của bạn. Đây là một trong những yếu tố quan trọng nhất mà người chơi cần hiểu.</p>

<h2>Đơn Vị Đo Lường</h2>
<p>Lực căng dây thường được đo bằng pound (lbs) hoặc kilogram. Phạm vi phổ biến từ 17-30 lbs.</p>

<h2>Phân Loại Lực Căng</h2>

<h3>Căng Nhẹ (17-22 lbs)</h3>
<ul>
<li>Tạo sức mạnh đàn hồi tốt hơn</li>
<li>Vùng ngọt rộng hơn (dễ đánh)</li>
<li>Phù hợp người mới và trung cấp</li>
<li>Ít tổn hao năng lượng</li>
</ul>

<h3>Căng Trung (22-26 lbs)</h3>
<ul>
<li>Cân bằng giữa sức mạnh và kiểm soát</li>
<li>Phù hợp người chơi trung cấp trở lên</li>
<li>Thông dụng nhất trong cộng đồng</li>
</ul>

<h3>Căng Cao (26-30 lbs)</h3>
<ul>
<li>Kiểm soát tuyệt vời</li>
<li>Cảm giác cầu rõ ràng hơn</li>
<li>Chỉ phù hợp người chơi nâng cao/chuyên nghiệp</li>
<li>Đòi hỏi kỹ thuật đánh đúng</li>
</ul>

<h2>Lời Khuyên Thực Tế</h2>
<p>Người mới bắt đầu nên căng ở mức 20-22 lbs. Khi kỹ thuật tốt hơn, bạn có thể tăng dần lên. Đừng căng quá mức khuyến nghị của nhà sản xuất vì có thể làm hỏng vợt.</p>

<h2>Tần Suất Căng Lại</h2>
<p>Dây cầu lông mất độ căng theo thời gian. Người chơi thường xuyên (3-4 buổi/tuần) nên căng lại mỗi 2-3 tháng. Ngay cả khi không chơi, dây vẫn giảm căng khoảng 10% sau mỗi 3 tháng.</p>''',
            'meta_title': 'Lực Căng Dây Cầu Lông Bao Nhiêu Là Phù Hợp? | CầuLong.com',
            'meta_description': 'Tìm hiểu về lực căng dây cầu lông - căng bao nhiêu lbs là phù hợp với trình độ của bạn? Hướng dẫn chi tiết từ người mới đến chuyên nghiệp.',
            'is_published': True,
        },
        {
            'title': 'Top 10 Vợt Cầu Lông Tốt Nhất Năm 2024',
            'content': '''<h2>Tiêu Chí Đánh Giá</h2>
<p>Danh sách này được tổng hợp dựa trên các tiêu chí: chất lượng vật liệu, hiệu suất đánh cầu, độ bền, giá trị đồng tiền và phản hồi từ cộng đồng người chơi.</p>

<h2>Top 10 Vợt Tốt Nhất 2024</h2>

<h3>1. Yonex Astrox 99 Pro</h3>
<p>Được sử dụng bởi Kento Momota, đây là vợt tốt nhất cho người chơi chuyên nghiệp thích tấn công. Sức mạnh smash không có đối thủ.</p>

<h3>2. Victor Thruster K 9900</h3>
<p>Cạnh tranh trực tiếp với Astrox 99 Pro, Victor Thruster K 9900 mang lại sức mạnh tương đương với giá cạnh tranh hơn.</p>

<h3>3. Yonex Nanoflare 1000Z</h3>
<p>Vợt tốc độ số 1, sử dụng sợi carbon Torayca M40X đắt tiền. Lý tưởng cho lối chơi nhanh và linh hoạt.</p>

<h3>4. Li-Ning Tectonic 9</h3>
<p>Lựa chọn hàng đầu của đội tuyển Trung Quốc, kết hợp sức mạnh và công nghệ tiên tiến.</p>

<h3>5. Victor Jetspeed S 12 II</h3>
<p>Tốc độ vượt trội trong phân khúc cao cấp từ Victor, phù hợp đôi nam và đơn nữ.</p>

<h3>6. Yonex Astrox 88D Pro</h3>
<p>Vợt đôi tốt nhất, được thiết kế đặc biệt cho người chơi vị trí đánh phía sau.</p>

<h3>7. Mizuno Altius 01</h3>
<p>Đại diện chất lượng Nhật Bản, với công nghệ DiamondCore độc quyền và độ bền vượt trội.</p>

<h3>8. Yonex Arcsaber 11 Pro</h3>
<p>Vợt toàn diện nhất của Yonex, phù hợp người chơi không muốn thiên về tấn công hay phòng thủ.</p>

<h3>9. Victor Hypernano X 900</h3>
<p>Lựa chọn tốt trong phân khúc tầm trung của Victor với công nghệ Hard Cored Technology.</p>

<h3>10. Apacs Lethal 10</h3>
<p>Giá trị tốt nhất: sức mạnh tốt, thiết kế đẹp với mức giá phải chăng hơn nhiều so với các thương hiệu lớn.</p>

<h2>Kết Luận</h2>
<p>Không có một cây vợt nào là "tốt nhất" cho tất cả mọi người. Hãy chọn vợt phù hợp với trình độ và phong cách chơi của bạn!</p>''',
            'meta_title': 'Top 10 Vợt Cầu Lông Tốt Nhất 2024 | CầuLong.com',
            'meta_description': 'Danh sách 10 vợt cầu lông tốt nhất năm 2024 từ Yonex, Victor, Li-Ning và các thương hiệu hàng đầu. Đánh giá chi tiết và xếp hạng.',
            'is_published': True,
        },
        {
            'title': 'Cách Bảo Quản Vợt Cầu Lông Đúng Cách',
            'content': '''<h2>Tại Sao Cần Bảo Quản Vợt Đúng Cách?</h2>
<p>Một cây vợt cầu lông chất lượng cao có thể có giá hàng triệu đồng. Bảo quản đúng cách không chỉ giúp vợt bền hơn mà còn duy trì hiệu suất đánh cầu ổn định.</p>

<h2>Những Điều Nên Làm</h2>

<h3>1. Sử Dụng Bao Vợt</h3>
<p>Luôn đựng vợt trong bao vợt chuyên dụng sau khi chơi xong. Bao vợt bảo vệ khung khỏi va đập và trầy xước.</p>

<h3>2. Bảo Quản Ở Nhiệt Độ Phù Hợp</h3>
<p>Tránh để vợt ở những nơi nhiệt độ cao như trong xe ô tô dưới nắng. Nhiệt độ cao có thể làm biến dạng khung và suy giảm chất lượng dây.</p>

<h3>3. Giữ Độ Ẩm Ổn Định</h3>
<p>Không để vợt ở nơi quá ẩm hoặc quá khô. Độ ẩm cao có thể làm han gỉ các bộ phận kim loại.</p>

<h3>4. Kiểm Tra Dây Định Kỳ</h3>
<p>Kiểm tra dây thường xuyên để phát hiện sớm các dấu hiệu mòn hoặc đứt. Thay dây kịp thời để tránh ảnh hưởng đến hiệu suất.</p>

<h2>Những Điều Không Nên Làm</h2>
<ul>
<li>Không để vợt dưới ánh nắng trực tiếp trong thời gian dài</li>
<li>Không đặt vật nặng lên vợt</li>
<li>Không vung vợt mạnh vào bề mặt cứng khi tức giận</li>
<li>Không để vợt tiếp xúc với hóa chất tẩy rửa</li>
</ul>

<h2>Vệ Sinh Vợt</h2>
<p>Sau mỗi buổi chơi, lau nhẹ khung và cán bằng khăn ẩm. Tránh dùng hóa chất mạnh có thể ăn mòn vật liệu. Kiểm tra tay cầm định kỳ và thay khi đã mòn.</p>

<h2>Bảo Quản Dài Hạn</h2>
<p>Nếu không chơi trong thời gian dài, nên nới lỏng lực căng dây để giảm áp lực lên khung. Bảo quản ở nơi khô ráo, thoáng mát.</p>''',
            'meta_title': 'Cách Bảo Quản Vợt Cầu Lông Đúng Cách | CầuLong.com',
            'meta_description': 'Hướng dẫn bảo quản vợt cầu lông đúng cách để duy trì hiệu suất và kéo dài tuổi thọ của vợt.',
            'is_published': True,
        },
    ]

    for pd in posts_data:
        slug = generate_slug(pd['title'])
        p = BlogPost.query.filter_by(slug=slug).first()
        if not p:
            p = BlogPost(
                title=pd['title'],
                slug=slug,
                content=pd['content'],
                author_id=admin.id,
                meta_title=pd.get('meta_title', pd['title']),
                meta_description=pd.get('meta_description', ''),
                is_published=pd.get('is_published', True),
            )
            db.session.add(p)
            print(f'Created blog post: {pd["title"][:50]}')

    db.session.flush()

    # ── Reviews ─────────────────────────────────────────────────────────
    reviews_data = [
        {'racket_name': 'Yonex Astrox 88D Pro', 'rating': 5, 'title': 'Vợt đánh đôi xuất sắc', 'content': 'Sau 3 tháng sử dụng, tôi thực sự ấn tượng với sức mạnh smash của Astrox 88D Pro. Vợt phù hợp hoàn hảo cho vị trí đánh phía sau trong đôi nam.'},
        {'racket_name': 'Yonex Astrox 88D Pro', 'rating': 4, 'title': 'Tốt nhưng cần kỹ thuật', 'content': 'Vợt rất tốt nhưng đòi hỏi kỹ thuật cao. Lúc đầu tôi gặp khó khăn nhưng dần quen và hiệu quả tốt hơn nhiều.'},
        {'racket_name': 'Victor Thruster K 9900', 'rating': 5, 'title': 'Smash cực mạnh', 'content': 'Victor Thruster K 9900 là một cây vợt đỉnh. Smash của tôi tăng rõ rệt sau khi chuyển sang dùng vợt này.'},
        {'racket_name': 'Yonex Astrox 99 Pro', 'rating': 5, 'title': 'Vợt của nhà vô địch', 'content': 'Hiểu sao Momota dùng vợt này. Cảm giác đánh cầu tuyệt vời, sức mạnh và kiểm soát đều ở đỉnh cao.'},
        {'racket_name': 'Li-Ning Tectonic 9', 'rating': 4, 'title': 'Công nghệ Trung Quốc ấn tượng', 'content': 'Li-Ning đã tiến bộ vượt bậc. Tectonic 9 thực sự là vợt đáng để thử cho những ai muốn cảm giác smash mạnh.'},
        {'racket_name': 'Victor Jetspeed S 12 II', 'rating': 5, 'title': 'Tốc độ số 1', 'content': 'Chưa bao giờ cảm thấy vợt vung nhanh đến vậy. Hoàn hảo cho lối chơi tốc độ cao.'},
        {'racket_name': 'Yonex Nanoflare 1000Z', 'rating': 4, 'title': 'Tốc độ ấn tượng', 'content': 'Vợt nhẹ, tốc độ xuất sắc. Tuy nhiên smash không mạnh bằng dòng Astrox. Phù hợp với lối chơi của tôi.'},
        {'racket_name': 'Apacs Lethal 10', 'rating': 4, 'title': 'Giá trị tốt', 'content': 'Giá rẻ hơn nhiều so với Yonex hay Victor nhưng chất lượng không kém. Rất đáng tiền cho người chơi trung cấp.'},
        {'racket_name': 'Victor DriveX 10 Meta', 'rating': 3, 'title': 'Vợt ổn cho người mới lên trung cấp', 'content': 'Không có gì đặc biệt nhưng làm tốt công việc của nó. Phù hợp trong giai đoạn học kỹ thuật.'},
        {'racket_name': 'Yonex Arcsaber 11 Pro', 'rating': 5, 'title': 'Vợt toàn diện nhất tôi từng dùng', 'content': 'Arcsaber 11 Pro làm hài lòng tôi ở mọi phương diện. Không quá thiên về tấn công hay phòng thủ, rất phù hợp với phong cách của tôi.'},
    ]

    for rd_data in reviews_data:
        racket_slug = generate_slug(rd_data['racket_name'])
        racket = Racket.query.filter_by(slug=racket_slug).first()
        if racket and not Review.query.filter_by(racket_id=racket.id, title=rd_data['title']).first():
            review = Review(
                racket_id=racket.id,
                user_id=admin.id,
                rating=rd_data['rating'],
                title=rd_data['title'],
                content=rd_data['content'],
            )
            db.session.add(review)
            print(f'Created review for: {rd_data["racket_name"]}')

    db.session.commit()
    print('\n✓ Seed data created successfully!')
    print('  Admin: username=admin, password=admin123')
    print(f'  Brands: {Brand.query.count()}')
    print(f'  Rackets: {Racket.query.count()}')
    print(f'  Blog posts: {BlogPost.query.count()}')
    print(f'  Reviews: {Review.query.count()}')


if __name__ == '__main__':
    from app import create_app
    app = create_app()
    with app.app_context():
        seed_all()
