-- phpMyAdmin SQL Dump
-- version 5.2.3
-- https://www.phpmyadmin.net/
--
-- Vært: mariadb
-- Genereringstid: 12. 11 2025 kl. 07:32:14
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
-- Struktur-dump for tabellen `users`
--

CREATE TABLE `users` (
  `user_pk` bigint(20) UNSIGNED NOT NULL,
  `user_first_name` varchar(20) NOT NULL,
  `user_last_name` varchar(20) NOT NULL,
  `user_username` varchar(20) NOT NULL,
  `user_email` varchar(100) NOT NULL,
  `user_password` varchar(255) NOT NULL,
  `user_banner` varchar(100) NOT NULL,
  `user_avatar` varchar(100) NOT NULL,
  `user_bio` varchar(200) NOT NULL,
  `user_total_followers` bigint(20) UNSIGNED NOT NULL DEFAULT 0,
  `user_total_following` bigint(20) UNSIGNED NOT NULL DEFAULT 0,
  `user_total_likes` bigint(20) UNSIGNED NOT NULL DEFAULT 0,
  `user_total_posts` bigint(20) UNSIGNED NOT NULL,
  `user_created_at` bigint(20) UNSIGNED NOT NULL,
  `user_varified_at` bigint(20) UNSIGNED NOT NULL,
  `user_updated_at` bigint(20) UNSIGNED NOT NULL,
  `user_deletet_at` bigint(20) UNSIGNED NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Data dump for tabellen `users`
--

INSERT INTO `users` (`user_pk`, `user_first_name`, `user_last_name`, `user_username`, `user_email`, `user_password`, `user_banner`, `user_avatar`, `user_bio`, `user_total_followers`, `user_total_following`, `user_total_likes`, `user_total_posts`, `user_created_at`, `user_varified_at`, `user_updated_at`, `user_deletet_at`) VALUES
(3, 'Luca', 'klæø', 'Lucakl', 'a@a.com', 'jlawdhjbawdbhjwadhjbadwbhjadwhjbadw', 'path:to.banner', 'path:to.avatar', 'cool bio', 1, 0, 1, 2, 1758708393, 0, 1758708393, 0),
(4, 'Luca', 'klæø', 'Lucakl', 'a@b.com', 'jlawdhjbawdbhjwadhjbadwbhjadwhjbadw', 'path:to.banner', 'path:to.avatar', 'cool bio 2', 0, 1, 0, 0, 1758708393, 0, 1758708393, 0);

--
-- Begrænsninger for dumpede tabeller
--

--
-- Indeks for tabel `users`
--
ALTER TABLE `users`
  ADD PRIMARY KEY (`user_pk`),
  ADD UNIQUE KEY `user_pk` (`user_pk`),
  ADD UNIQUE KEY `user_username` (`user_username`,`user_email`);

--
-- Brug ikke AUTO_INCREMENT for slettede tabeller
--

--
-- Tilføj AUTO_INCREMENT i tabel `users`
--
ALTER TABLE `users`
  MODIFY `user_pk` bigint(20) UNSIGNED NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=5;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
