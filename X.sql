-- phpMyAdmin SQL Dump
-- version 5.2.3
-- https://www.phpmyadmin.net/
--
-- Vært: mariadb
-- Genereringstid: 17. 11 2025 kl. 05:25:24
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
-- Struktur-dump for tabellen `comments`
--

CREATE TABLE `comments` (
  `comment_pk` bigint(20) UNSIGNED NOT NULL,
  `post_fk` bigint(20) UNSIGNED NOT NULL,
  `user_fk` bigint(20) UNSIGNED NOT NULL,
  `comment_message` varchar(100) NOT NULL,
  `comment_created_at` bigint(20) UNSIGNED NOT NULL,
  `comment_updated_at` bigint(20) UNSIGNED NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

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
WHERE user_pk = OLD.user_follows_fk
$$
DELIMITER ;
DELIMITER $$
CREATE TRIGGER `user_total_followeing_incresse` AFTER INSERT ON `followers` FOR EACH ROW UPDATE users
SET user_total_following = user_total_following + 1
WHERE user_pk = NEW.user_follows_fk
$$
DELIMITER ;
DELIMITER $$
CREATE TRIGGER `user_total_followers_decresse` AFTER DELETE ON `followers` FOR EACH ROW UPDATE users
SET user_total_followers = user_total_followers - 1
WHERE user_pk = OLD.user_fk
$$
DELIMITER ;
DELIMITER $$
CREATE TRIGGER `user_total_followers_incresse` AFTER INSERT ON `followers` FOR EACH ROW UPDATE users
SET user_total_followers = user_total_followers + 1
WHERE user_pk = NEW.user_fk
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
WHERE user_pk = OLD.user_fk
$$
DELIMITER ;
DELIMITER $$
CREATE TRIGGER `user_total_likes_incresse` AFTER INSERT ON `likes` FOR EACH ROW UPDATE users
SET user_total_likes = user_total_likes + 1
WHERE user_pk = NEW.user_fk
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
  `post_total_comments` bigint(20) UNSIGNED NOT NULL,
  `post_total_likes` bigint(20) UNSIGNED NOT NULL,
  `post_total_saved` bigint(20) UNSIGNED NOT NULL,
  `post_created_at` bigint(20) UNSIGNED NOT NULL,
  `post_updated_at` bigint(20) UNSIGNED NOT NULL,
  `post_deleted_at` bigint(20) UNSIGNED NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

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
-- Struktur-dump for tabellen `posts_media`
--

CREATE TABLE `posts_media` (
  `post_fk` bigint(20) UNSIGNED NOT NULL,
  `post_media_path` varchar(100) NOT NULL,
  `posts_media_type_fk` bigint(3) UNSIGNED NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Struktur-dump for tabellen `posts_media_types`
--

CREATE TABLE `posts_media_types` (
  `posts_media_type_pk` bigint(20) UNSIGNED NOT NULL,
  `posts_media_type_type` varchar(10) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Data dump for tabellen `posts_media_types`
--

INSERT INTO `posts_media_types` (`posts_media_type_pk`, `posts_media_type_type`) VALUES
(1, 'image'),
(2, 'video'),
(3, 'file');

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
-- Struktur-dump for tabellen `saves`
--

CREATE TABLE `saves` (
  `user_fk` bigint(20) UNSIGNED NOT NULL,
  `post_fk` bigint(20) UNSIGNED NOT NULL,
  `save_created_at` bigint(20) UNSIGNED NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Triggers/udløsere `saves`
--
DELIMITER $$
CREATE TRIGGER `post_total_saved_decresse` BEFORE DELETE ON `saves` FOR EACH ROW UPDATE posts
SET post_total_saved = post_total_saved - 1
WHERE post_pk = OLD.post_fk
$$
DELIMITER ;
DELIMITER $$
CREATE TRIGGER `post_total_saved_incresse` AFTER INSERT ON `saves` FOR EACH ROW UPDATE posts
SET post_total_saved = post_total_saved + 1
WHERE post_pk = NEW.post_fk
$$
DELIMITER ;

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
  `user_deletet_at` bigint(20) UNSIGNED NOT NULL DEFAULT 0
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Data dump for tabellen `users`
--

INSERT INTO `users` (`user_pk`, `user_first_name`, `user_last_name`, `user_username`, `user_email`, `user_password`, `user_language`, `role_fk`, `user_banner`, `user_avatar`, `user_bio`, `user_total_followers`, `user_total_following`, `user_total_likes`, `user_total_posts`, `user_created_at`, `user_varified_at`, `user_updated_at`, `user_deletet_at`) VALUES
(10, 'luca', 'klæø', 'lucakl', 'lucaklaeoe@gmail.com', 'scrypt:32768:8:1$6NmFWjNGnCMRYqyh$3642d4ae60ebe0e3a602b965d8aefc1dbcb4a0a28d9b2214c848f0e5b76813a8f7bf890e53751edba25dd0eca91d1602a83b86c8bf3cbb82abe87dcf709885c4', 'english', 2, 'default_banner.jpg', 'default.svg', 'No bio', 0, 0, 0, 0, 1763160252, 1763244248, 0, 0),
(21, 'Luca', 'Klæø', 'tester', 'a@b.com', 'scrypt:32768:8:1$wWl0mOYaUXQBJxd6$17e50b0290403c1f943c501be90d406501beb714b7337c85b5045d0b17a39e4b4d081632ba9ca9f95ccd0cfe3275399a3532c040500369107a75ccab5c173a33', 'english', 1, 'default_banner.jpg', 'default.svg', 'No bio', 0, 0, 0, 0, 1763234764, 1763234764, 0, 0);

--
-- Begrænsninger for dumpede tabeller
--

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
-- Indeks for tabel `posts_media`
--
ALTER TABLE `posts_media`
  ADD PRIMARY KEY (`post_fk`,`post_media_path`),
  ADD KEY `post_media_type_pfk` (`posts_media_type_fk`);

--
-- Indeks for tabel `posts_media_types`
--
ALTER TABLE `posts_media_types`
  ADD PRIMARY KEY (`posts_media_type_pk`),
  ADD UNIQUE KEY `posts_media_type_pk` (`posts_media_type_pk`);

--
-- Indeks for tabel `roles`
--
ALTER TABLE `roles`
  ADD UNIQUE KEY `role_pk` (`role_pk`);

--
-- Indeks for tabel `saves`
--
ALTER TABLE `saves`
  ADD PRIMARY KEY (`user_fk`,`post_fk`),
  ADD KEY `save_post_pfk` (`post_fk`);

--
-- Indeks for tabel `users`
--
ALTER TABLE `users`
  ADD PRIMARY KEY (`user_pk`),
  ADD UNIQUE KEY `user_pk` (`user_pk`),
  ADD UNIQUE KEY `user_email` (`user_email`),
  ADD UNIQUE KEY `user_username` (`user_username`),
  ADD KEY `role_fk` (`role_fk`);

--
-- Brug ikke AUTO_INCREMENT for slettede tabeller
--

--
-- Tilføj AUTO_INCREMENT i tabel `comments`
--
ALTER TABLE `comments`
  MODIFY `comment_pk` bigint(20) UNSIGNED NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;

--
-- Tilføj AUTO_INCREMENT i tabel `posts`
--
ALTER TABLE `posts`
  MODIFY `post_pk` bigint(20) UNSIGNED NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=11;

--
-- Tilføj AUTO_INCREMENT i tabel `posts_media_types`
--
ALTER TABLE `posts_media_types`
  MODIFY `posts_media_type_pk` bigint(20) UNSIGNED NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4;

--
-- Tilføj AUTO_INCREMENT i tabel `roles`
--
ALTER TABLE `roles`
  MODIFY `role_pk` bigint(20) UNSIGNED NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;

--
-- Tilføj AUTO_INCREMENT i tabel `users`
--
ALTER TABLE `users`
  MODIFY `user_pk` bigint(20) UNSIGNED NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=22;

--
-- Begrænsninger for dumpede tabeller
--

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
-- Begrænsninger for tabel `posts_media`
--
ALTER TABLE `posts_media`
  ADD CONSTRAINT `post_media_type_pfk` FOREIGN KEY (`posts_media_type_fk`) REFERENCES `posts_media_types` (`posts_media_type_pk`) ON DELETE CASCADE ON UPDATE CASCADE,
  ADD CONSTRAINT `posts_media_post_pfk` FOREIGN KEY (`post_fk`) REFERENCES `posts` (`post_pk`) ON DELETE CASCADE ON UPDATE CASCADE;

--
-- Begrænsninger for tabel `saves`
--
ALTER TABLE `saves`
  ADD CONSTRAINT `save_post_pfk` FOREIGN KEY (`post_fk`) REFERENCES `posts` (`post_pk`) ON DELETE CASCADE ON UPDATE CASCADE,
  ADD CONSTRAINT `save_user_pfk` FOREIGN KEY (`user_fk`) REFERENCES `users` (`user_pk`) ON DELETE CASCADE ON UPDATE CASCADE;

--
-- Begrænsninger for tabel `users`
--
ALTER TABLE `users`
  ADD CONSTRAINT `role_user_pfk` FOREIGN KEY (`role_fk`) REFERENCES `roles` (`role_pk`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
