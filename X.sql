-- phpMyAdmin SQL Dump
-- version 5.2.3
-- https://www.phpmyadmin.net/
--
-- Vært: mariadb
-- Genereringstid: 24. 11 2025 kl. 21:47:43
-- Serverversion: 10.6.20-MariaDB-ubu2004
-- PHP-version: 8.3.26

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `x`
--

-- --------------------------------------------------------

--
-- Struktur-dump for tabellen `bookmarks`
--

CREATE TABLE `bookmarks` (
  `user_fk` bigint(20) UNSIGNED NOT NULL,
  `post_fk` bigint(20) UNSIGNED NOT NULL,
  `save_created_at` bigint(20) UNSIGNED NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Data dump for tabellen `bookmarks`
--

INSERT INTO `bookmarks` (`user_fk`, `post_fk`, `save_created_at`) VALUES
(10, 37, 1763906348),
(10, 38, 1763906346),
(10, 39, 1763906345),
(10, 40, 1763906345),
(10, 41, 1763906343),
(10, 48, 1763906343),
(10, 54, 1763904797);

--
-- Triggers/udløsere `bookmarks`
--
DELIMITER $$
CREATE TRIGGER `post_total_saved_decresse` BEFORE DELETE ON `bookmarks` FOR EACH ROW UPDATE posts
SET post_total_bookmark = post_total_bookmark - 1
WHERE post_pk = OLD.post_fk
$$
DELIMITER ;
DELIMITER $$
CREATE TRIGGER `post_total_saved_incresse` AFTER INSERT ON `bookmarks` FOR EACH ROW UPDATE posts
SET post_total_bookmark = post_total_bookmark + 1
WHERE post_pk = NEW.post_fk
$$
DELIMITER ;

-- --------------------------------------------------------

--
-- Struktur-dump for tabellen `comments`
--

CREATE TABLE `comments` (
  `comment_pk` bigint(20) UNSIGNED NOT NULL,
  `post_fk` bigint(20) UNSIGNED NOT NULL,
  `user_fk` bigint(20) UNSIGNED NOT NULL,
  `comment_message` varchar(100) NOT NULL,
  `comment_created_at` bigint(20) UNSIGNED NOT NULL,
  `comment_updated_at` bigint(20) UNSIGNED NOT NULL DEFAULT 0
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Data dump for tabellen `comments`
--

INSERT INTO `comments` (`comment_pk`, `post_fk`, `user_fk`, `comment_message`, `comment_created_at`, `comment_updated_at`) VALUES
(11, 49, 10, 'test post', 1763854553, 0),
(32, 54, 10, 'another comment in the matrix', 1763903592, 0);

--
-- Triggers/udløsere `comments`
--
DELIMITER $$
CREATE TRIGGER `post_total_comments_decreese` AFTER DELETE ON `comments` FOR EACH ROW UPDATE posts
SET post_total_comments = post_total_comments - 1
WHERE post_pk = OLD.post_fk
$$
DELIMITER ;
DELIMITER $$
CREATE TRIGGER `post_total_comments_incresse` AFTER INSERT ON `comments` FOR EACH ROW UPDATE posts
SET post_total_comments = post_total_comments + 1
WHERE post_pk = NEW.post_fk
$$
DELIMITER ;

-- --------------------------------------------------------

--
-- Struktur-dump for tabellen `followers`
--

CREATE TABLE `followers` (
  `user_fk` bigint(20) UNSIGNED NOT NULL,
  `user_follows_fk` bigint(20) UNSIGNED NOT NULL,
  `follower_created_at` bigint(20) UNSIGNED NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Triggers/udløsere `followers`
--
DELIMITER $$
CREATE TRIGGER `user_total_followeing_decresse` AFTER DELETE ON `followers` FOR EACH ROW UPDATE users
SET user_total_following = user_total_following - 1
WHERE user_pk = OLD.user_fk
$$
DELIMITER ;
DELIMITER $$
CREATE TRIGGER `user_total_followeing_incresse` AFTER INSERT ON `followers` FOR EACH ROW UPDATE users
SET user_total_following = user_total_following + 1
WHERE user_pk = NEW.user_fk
$$
DELIMITER ;
DELIMITER $$
CREATE TRIGGER `user_total_followers_decresse` AFTER DELETE ON `followers` FOR EACH ROW UPDATE users
SET user_total_followers = user_total_followers - 1
WHERE user_pk = OLD.user_follows_fk
$$
DELIMITER ;
DELIMITER $$
CREATE TRIGGER `user_total_followers_incresse` AFTER INSERT ON `followers` FOR EACH ROW UPDATE users
SET user_total_followers = user_total_followers + 1
WHERE user_pk = NEW.user_follows_fk
$$
DELIMITER ;

-- --------------------------------------------------------

--
-- Struktur-dump for tabellen `likes`
--

CREATE TABLE `likes` (
  `user_fk` bigint(20) UNSIGNED NOT NULL,
  `post_fk` bigint(20) UNSIGNED NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Data dump for tabellen `likes`
--

INSERT INTO `likes` (`user_fk`, `post_fk`) VALUES
(10, 38),
(10, 54),
(21, 38),
(21, 54);

--
-- Triggers/udløsere `likes`
--
DELIMITER $$
CREATE TRIGGER `post_total_likes_decresse` AFTER DELETE ON `likes` FOR EACH ROW UPDATE posts
SET post_total_likes = post_total_likes - 1
WHERE post_pk = OLD.post_fk
$$
DELIMITER ;
DELIMITER $$
CREATE TRIGGER `post_total_likes_incresse` AFTER INSERT ON `likes` FOR EACH ROW UPDATE posts
SET post_total_likes = post_total_likes + 1
WHERE post_pk = NEW.post_fk
$$
DELIMITER ;
DELIMITER $$
CREATE TRIGGER `user_total_likes_decresse` AFTER DELETE ON `likes` FOR EACH ROW UPDATE users
SET user_total_likes = user_total_likes - 1
WHERE user_pk = (SELECT user_fk FROM posts WHERE post_pk = OLD.post_fk LIMIT 1)
$$
DELIMITER ;
DELIMITER $$
CREATE TRIGGER `user_total_likes_incresse` AFTER INSERT ON `likes` FOR EACH ROW UPDATE users
SET user_total_likes = user_total_likes + 1
WHERE user_pk = (SELECT user_fk FROM posts WHERE post_pk = NEW.post_fk LIMIT 1)
$$
DELIMITER ;

-- --------------------------------------------------------

--
-- Struktur-dump for tabellen `not_verifyed_accounts`
--

CREATE TABLE `not_verifyed_accounts` (
  `user_fk` bigint(20) UNSIGNED NOT NULL,
  `uuid` char(32) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Struktur-dump for tabellen `posts`
--

CREATE TABLE `posts` (
  `post_pk` bigint(20) UNSIGNED NOT NULL,
  `user_fk` bigint(20) UNSIGNED NOT NULL,
  `post_message` varchar(200) NOT NULL,
  `post_total_comments` bigint(20) UNSIGNED NOT NULL DEFAULT 0,
  `post_total_likes` bigint(20) UNSIGNED NOT NULL DEFAULT 0,
  `post_total_bookmark` bigint(20) UNSIGNED NOT NULL DEFAULT 0,
  `post_created_at` bigint(20) UNSIGNED NOT NULL,
  `post_updated_at` bigint(20) UNSIGNED NOT NULL DEFAULT 0,
  `post_deleted_at` bigint(20) UNSIGNED NOT NULL DEFAULT 0
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Data dump for tabellen `posts`
--

INSERT INTO `posts` (`post_pk`, `user_fk`, `post_message`, `post_total_comments`, `post_total_likes`, `post_total_bookmark`, `post_created_at`, `post_updated_at`, `post_deleted_at`) VALUES
(11, 10, 'This is a post', 0, 0, 0, 1231213321, 0, 0),
(12, 10, 'This is a test for time', 0, 0, 0, 1763455801, 1763455826, 0),
(13, 21, 'HEJ!', 0, 0, 0, 1763650562, 0, 0),
(14, 21, 'HEJ!', 0, 0, 0, 1763650586, 0, 0),
(15, 21, 'TEST', 0, 0, 0, 1763650869, 0, 0),
(16, 21, 'another post in the matrix', 0, 0, 0, 1763650943, 0, 0),
(17, 10, 'test fore files', 0, 0, 0, 1763657024, 0, 0),
(18, 10, 'test fore files1', 0, 0, 0, 1763657081, 0, 0),
(19, 10, 'file test2', 0, 0, 0, 1763657904, 0, 0),
(20, 10, 'file test3', 0, 0, 0, 1763658063, 0, 0),
(21, 10, 'file test4', 0, 0, 0, 1763658082, 0, 0),
(22, 10, 'file test5', 0, 0, 0, 1763658148, 0, 0),
(23, 10, 'file test6', 0, 0, 0, 1763662140, 0, 0),
(24, 10, 'file test7', 0, 0, 0, 1763662160, 0, 0),
(25, 10, 'file test8', 0, 0, 0, 1763662315, 0, 0),
(26, 10, 'file test9', 0, 0, 0, 1763662357, 0, 0),
(33, 10, 'file test10', 0, 0, 0, 1763664712, 0, 0),
(34, 10, 'file test11', 0, 0, 0, 1763664785, 0, 0),
(35, 10, 'file test12', 0, 0, 0, 1763664805, 0, 0),
(36, 10, 'file test13', 0, 0, 0, 1763664825, 0, 0),
(37, 10, 'file test 13', 0, 0, 1, 1763664884, 0, 0),
(38, 10, 'file test 14', 0, 2, 1, 1763664910, 0, 0),
(39, 21, 'i am posteing some more to see auto schroll works on profile', 0, 0, 1, 1763779116, 0, 0),
(40, 21, 'i am posteing some more to see auto schroll works on profile', 0, 0, 1, 1763779212, 0, 0),
(41, 21, 'i am posteing some more to see auto schroll works on profile 2', 0, 0, 1, 1763779257, 0, 0),
(42, 21, 'i am posteing some more to see auto schroll works on profile 3', 0, 0, 0, 1763779279, 0, 1763857314),
(43, 21, 'i am posteing some more to see auto schroll works on profile 5', 0, 0, 0, 1763779294, 0, 1763857312),
(44, 21, 'i am posteing some more to see auto schroll works on profile 6', 0, 0, 0, 1763779330, 0, 1763857311),
(45, 21, 'i am posteing some more to see auto schroll works on profile 7', 0, 0, 0, 1763779343, 0, 1763857310),
(46, 21, 'i am posteing some more to see auto schroll works on profile 8', 0, 0, 0, 1763779373, 0, 1763857296),
(47, 21, 'i am posteing some more to see auto schroll works on profile 9', 0, 0, 0, 1763779402, 0, 1763857318),
(48, 21, 'i am posteing some more to see auto schroll works on profile 10', 0, 0, 1, 1763779439, 0, 0),
(49, 21, 'i am posteing some more to see auto schroll works on profile 10', 1, 0, 0, 1763779454, 0, 1763856160),
(50, 21, 'i am posteing some more to se', 0, 0, 0, 1763779485, 1763841074, 1763841087),
(51, 21, 'this is', 0, 0, 0, 1763779561, 1763840836, 1763840844),
(52, 21, 'i am posteing some more to see auto schroll works on profile 13', 0, 0, 0, 1763779565, 0, 1763834527),
(53, 21, 'i am posteing some more to see auto schroll works on profile 13', 0, 0, 0, 1763779568, 0, 1763834454),
(54, 22, 'this is a post from a third account', 1, 2, 1, 1763847898, 0, 0);

--
-- Triggers/udløsere `posts`
--
DELIMITER $$
CREATE TRIGGER `user_total_post_decreese` AFTER DELETE ON `posts` FOR EACH ROW UPDATE users
SET user_total_posts = user_total_posts - 1
WHERE user_pk = OLD.user_fk
$$
DELIMITER ;
DELIMITER $$
CREATE TRIGGER `user_total_post_incresse` AFTER INSERT ON `posts` FOR EACH ROW UPDATE users
SET user_total_posts = user_total_posts + 1
WHERE user_pk = NEW.user_fk
$$
DELIMITER ;

-- --------------------------------------------------------

--
-- Struktur-dump for tabellen `post_medias`
--

CREATE TABLE `post_medias` (
  `post_fk` bigint(20) UNSIGNED NOT NULL,
  `post_media_path` varchar(100) NOT NULL,
  `post_media_type_fk` bigint(3) UNSIGNED NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Data dump for tabellen `post_medias`
--

INSERT INTO `post_medias` (`post_fk`, `post_media_path`, `post_media_type_fk`) VALUES
(33, 'fd626678490d40d7aee668ee92c208b9.jpg', 1),
(34, '3905794e07464b37b1e7fe96c1f0069d.jpg', 1),
(35, 'ffa96c2febe541c7b6dc795db149c8a9.jpeg', 1),
(36, 'abf3ca8386ee4110973d06ec77bef6ff.mp4', 2),
(37, 'e017393aff6c4ec5bfe4c9f02b70b054.mp4', 2),
(50, 'f6f73dfa772d42188dcced05d44e6111.mp4', 2),
(51, 'c2d2ad990dbf420ea0d342a6b89fa2fb.mp4', 2),
(53, '042c7c5fc8ba4e97a400b2fae1966710.mp4', 2),
(38, 'f03ac07ad28a453aa255ad26fa201992.pdf', 3),
(49, 'bfaed9ac6e6a40168af3d8b98b88d320.pdf', 3);

-- --------------------------------------------------------

--
-- Struktur-dump for tabellen `post_media_types`
--

CREATE TABLE `post_media_types` (
  `post_media_type_pk` bigint(20) UNSIGNED NOT NULL,
  `post_media_type_type` varchar(10) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Data dump for tabellen `post_media_types`
--

INSERT INTO `post_media_types` (`post_media_type_pk`, `post_media_type_type`) VALUES
(1, 'image'),
(2, 'video'),
(3, 'file'),
(4, 'audio');

-- --------------------------------------------------------

--
-- Struktur-dump for tabellen `roles`
--

CREATE TABLE `roles` (
  `role_pk` bigint(20) UNSIGNED NOT NULL,
  `role_title` varchar(10) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Data dump for tabellen `roles`
--

INSERT INTO `roles` (`role_pk`, `role_title`) VALUES
(1, 'user'),
(2, 'admin');

-- --------------------------------------------------------

--
-- Struktur-dump for tabellen `users`
--

CREATE TABLE `users` (
  `user_pk` bigint(20) UNSIGNED NOT NULL,
  `user_first_name` varchar(20) NOT NULL,
  `user_last_name` varchar(20) NOT NULL,
  `user_username` varchar(20) NOT NULL,
  `user_email` varchar(100) NOT NULL,
  `user_password` varchar(255) NOT NULL,
  `user_language` varchar(10) NOT NULL DEFAULT 'english',
  `role_fk` bigint(20) UNSIGNED NOT NULL DEFAULT 1,
  `user_banner` varchar(100) NOT NULL DEFAULT 'default_banner.jpg',
  `user_avatar` varchar(100) NOT NULL DEFAULT 'default.svg',
  `user_bio` varchar(200) NOT NULL DEFAULT 'No bio',
  `user_total_followers` bigint(20) UNSIGNED NOT NULL DEFAULT 0,
  `user_total_following` bigint(20) UNSIGNED NOT NULL DEFAULT 0,
  `user_total_likes` bigint(20) UNSIGNED NOT NULL DEFAULT 0,
  `user_total_posts` bigint(20) UNSIGNED NOT NULL DEFAULT 0,
  `user_created_at` bigint(20) UNSIGNED NOT NULL,
  `user_varified_at` bigint(20) UNSIGNED NOT NULL DEFAULT 0,
  `user_updated_at` bigint(20) UNSIGNED NOT NULL DEFAULT 0,
  `user_deleted_at` bigint(20) UNSIGNED NOT NULL DEFAULT 0
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Data dump for tabellen `users`
--

INSERT INTO `users` (`user_pk`, `user_first_name`, `user_last_name`, `user_username`, `user_email`, `user_password`, `user_language`, `role_fk`, `user_banner`, `user_avatar`, `user_bio`, `user_total_followers`, `user_total_following`, `user_total_likes`, `user_total_posts`, `user_created_at`, `user_varified_at`, `user_updated_at`, `user_deleted_at`) VALUES
(10, 'luca', 'klæø', 'lucakl', 'lucaklaeoe@gmail.com', 'scrypt:32768:8:1$6NmFWjNGnCMRYqyh$3642d4ae60ebe0e3a602b965d8aefc1dbcb4a0a28d9b2214c848f0e5b76813a8f7bf890e53751edba25dd0eca91d1602a83b86c8bf3cbb82abe87dcf709885c4', 'english', 2, 'bc8f0cc276c645fa95dc14df8730e816.png', 'a3e841c8d2444217911bc43549673a44.jpeg', 'THIS IS A COOL BIO AND A LONG ONE TO TEST OF IT WORKS AND HOW SHIT GETS DONE', 0, 0, 2, 18, 1763160252, 1763244248, 1763900438, 0),
(21, 'test', 'man', 'tester', 'lucaklaeoeskole@gmail.com', 'scrypt:32768:8:1$wWl0mOYaUXQBJxd6$17e50b0290403c1f943c501be90d406501beb714b7337c85b5045d0b17a39e4b4d081632ba9ca9f95ccd0cfe3275399a3532c040500369107a75ccab5c173a33', 'english', 1, 'default_banner.jpg', 'df53c2b8faa04fcfb42ae81ae6a9251a.jpeg', 'No bio', 0, 0, 0, 19, 1763234764, 1763234764, 1763841113, 0),
(22, 'More', 'People', 'More', 'a@a.com', 'scrypt:32768:8:1$LCccAjL8wwGO1Z1K$3ab9a86f580458ed2a669d6c300936d0e8d3f0f9e694437c0897420cd3749785404f4226215bedd64a6515620a72d7e1b2322fd51ecdbfafcc9675d6d7ca23f9', 'english', 1, 'default_banner.jpg', 'default.svg', 'No bio', 0, 0, 2, 1, 1713847740, 1763847859, 0, 0),
(23, 'WOW', 'ME', 'xXwow_meXx', 'a@c.com', 'scrypt:32768:8:1$HdqtolqcuwR1BZii$d96afdb441e64c76f7a8328cac8800fc7a9d03e42155edd19f5a2bdbb097ad8fa50bdac3270deecd1fc89eb93147471f2e9507048aee59bcd8a1947f2303a5cb', 'english', 1, 'default_banner.jpg', 'default.svg', 'No bio', 0, 0, 0, 0, 1764007772, 1763847859, 0, 0),
(24, 'another', 'user', 'another_user', 'a@d.com', 'scrypt:32768:8:1$Ed9MiGB2E6jDzVyk$7f1e4dc240382541d59dde725d72cbcdbacc6b5bef0e5fc8306ff8d3da05ab926e2fae8b260b932b0c8ee0d56a2309c35d0781991df1efdb381731b98c2e5ce1', 'english', 1, 'default_banner.jpg', 'default.svg', 'No bio', 0, 0, 0, 0, 1764007812, 1763234764, 0, 0);

--
-- Begrænsninger for dumpede tabeller
--

--
-- Indeks for tabel `bookmarks`
--
ALTER TABLE `bookmarks`
  ADD PRIMARY KEY (`user_fk`,`post_fk`),
  ADD KEY `save_post_pfk` (`post_fk`);

--
-- Indeks for tabel `comments`
--
ALTER TABLE `comments`
  ADD PRIMARY KEY (`comment_pk`),
  ADD UNIQUE KEY `comment_pk` (`comment_pk`),
  ADD KEY `comment_user_pfk` (`user_fk`),
  ADD KEY `comment_post_pfk` (`post_fk`);

--
-- Indeks for tabel `followers`
--
ALTER TABLE `followers`
  ADD PRIMARY KEY (`user_fk`,`user_follows_fk`),
  ADD KEY `follower_user_pfk_2` (`user_follows_fk`);

--
-- Indeks for tabel `likes`
--
ALTER TABLE `likes`
  ADD PRIMARY KEY (`user_fk`,`post_fk`),
  ADD KEY `user_fk_2` (`user_fk`),
  ADD KEY `post_fk` (`post_fk`);

--
-- Indeks for tabel `not_verifyed_accounts`
--
ALTER TABLE `not_verifyed_accounts`
  ADD UNIQUE KEY `uuid` (`uuid`),
  ADD KEY `user_not_verifyed_accounts_pfk` (`user_fk`);

--
-- Indeks for tabel `posts`
--
ALTER TABLE `posts`
  ADD PRIMARY KEY (`post_pk`),
  ADD UNIQUE KEY `post_pk` (`post_pk`),
  ADD KEY `user_fk` (`user_fk`,`post_message`);
ALTER TABLE `posts` ADD FULLTEXT KEY `post_message` (`post_message`);

--
-- Indeks for tabel `post_medias`
--
ALTER TABLE `post_medias`
  ADD PRIMARY KEY (`post_fk`,`post_media_path`),
  ADD KEY `post_media_type_pfk` (`post_media_type_fk`);

--
-- Indeks for tabel `post_media_types`
--
ALTER TABLE `post_media_types`
  ADD PRIMARY KEY (`post_media_type_pk`),
  ADD UNIQUE KEY `posts_media_type_pk` (`post_media_type_pk`);

--
-- Indeks for tabel `roles`
--
ALTER TABLE `roles`
  ADD UNIQUE KEY `role_pk` (`role_pk`);

--
-- Indeks for tabel `users`
--
ALTER TABLE `users`
  ADD PRIMARY KEY (`user_pk`),
  ADD UNIQUE KEY `user_pk` (`user_pk`),
  ADD UNIQUE KEY `user_email` (`user_email`),
  ADD UNIQUE KEY `user_username` (`user_username`),
  ADD KEY `role_fk` (`role_fk`),
  ADD KEY `user_first_name` (`user_first_name`),
  ADD KEY `user_last_name` (`user_last_name`);

--
-- Brug ikke AUTO_INCREMENT for slettede tabeller
--

--
-- Tilføj AUTO_INCREMENT i tabel `comments`
--
ALTER TABLE `comments`
  MODIFY `comment_pk` bigint(20) UNSIGNED NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=33;

--
-- Tilføj AUTO_INCREMENT i tabel `posts`
--
ALTER TABLE `posts`
  MODIFY `post_pk` bigint(20) UNSIGNED NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=55;

--
-- Tilføj AUTO_INCREMENT i tabel `post_media_types`
--
ALTER TABLE `post_media_types`
  MODIFY `post_media_type_pk` bigint(20) UNSIGNED NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=5;

--
-- Tilføj AUTO_INCREMENT i tabel `roles`
--
ALTER TABLE `roles`
  MODIFY `role_pk` bigint(20) UNSIGNED NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;

--
-- Tilføj AUTO_INCREMENT i tabel `users`
--
ALTER TABLE `users`
  MODIFY `user_pk` bigint(20) UNSIGNED NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=25;

--
-- Begrænsninger for dumpede tabeller
--

--
-- Begrænsninger for tabel `bookmarks`
--
ALTER TABLE `bookmarks`
  ADD CONSTRAINT `save_post_pfk` FOREIGN KEY (`post_fk`) REFERENCES `posts` (`post_pk`) ON DELETE CASCADE ON UPDATE CASCADE,
  ADD CONSTRAINT `save_user_pfk` FOREIGN KEY (`user_fk`) REFERENCES `users` (`user_pk`) ON DELETE CASCADE ON UPDATE CASCADE;

--
-- Begrænsninger for tabel `comments`
--
ALTER TABLE `comments`
  ADD CONSTRAINT `comment_post_pfk` FOREIGN KEY (`post_fk`) REFERENCES `posts` (`post_pk`) ON DELETE CASCADE ON UPDATE CASCADE,
  ADD CONSTRAINT `comment_user_pfk` FOREIGN KEY (`user_fk`) REFERENCES `users` (`user_pk`) ON DELETE CASCADE ON UPDATE CASCADE;

--
-- Begrænsninger for tabel `followers`
--
ALTER TABLE `followers`
  ADD CONSTRAINT `follower_user_pfk_1` FOREIGN KEY (`user_fk`) REFERENCES `users` (`user_pk`) ON DELETE CASCADE ON UPDATE CASCADE,
  ADD CONSTRAINT `follower_user_pfk_2` FOREIGN KEY (`user_follows_fk`) REFERENCES `users` (`user_pk`) ON DELETE CASCADE ON UPDATE CASCADE;

--
-- Begrænsninger for tabel `likes`
--
ALTER TABLE `likes`
  ADD CONSTRAINT `like_post_pfk` FOREIGN KEY (`post_fk`) REFERENCES `posts` (`post_pk`),
  ADD CONSTRAINT `like_user_pfk` FOREIGN KEY (`user_fk`) REFERENCES `users` (`user_pk`) ON DELETE CASCADE ON UPDATE CASCADE;

--
-- Begrænsninger for tabel `not_verifyed_accounts`
--
ALTER TABLE `not_verifyed_accounts`
  ADD CONSTRAINT `user_not_verifyed_accounts_pfk` FOREIGN KEY (`user_fk`) REFERENCES `users` (`user_pk`) ON DELETE CASCADE ON UPDATE CASCADE;

--
-- Begrænsninger for tabel `posts`
--
ALTER TABLE `posts`
  ADD CONSTRAINT `post_user_pfk` FOREIGN KEY (`user_fk`) REFERENCES `users` (`user_pk`) ON DELETE CASCADE ON UPDATE CASCADE;

--
-- Begrænsninger for tabel `post_medias`
--
ALTER TABLE `post_medias`
  ADD CONSTRAINT `post_media_type_pfk` FOREIGN KEY (`post_media_type_fk`) REFERENCES `post_media_types` (`post_media_type_pk`) ON DELETE CASCADE ON UPDATE CASCADE,
  ADD CONSTRAINT `posts_media_post_pfk` FOREIGN KEY (`post_fk`) REFERENCES `posts` (`post_pk`) ON DELETE CASCADE ON UPDATE CASCADE;

--
-- Begrænsninger for tabel `users`
--
ALTER TABLE `users`
  ADD CONSTRAINT `role_user_pfk` FOREIGN KEY (`role_fk`) REFERENCES `roles` (`role_pk`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
