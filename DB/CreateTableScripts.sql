CREATE TABLE `airbnb_listing_details_japan_tokyo` (
  `id` bigint NOT NULL,
  `city` text,
  `user_id` text,
  `price` text,
  `country` text,
  `state` text,
  `person_capacity` text,
  `zipcode` text,
  `cancel_policy` text,
  `reviews_count` text,
  PRIMARY KEY (`id`)
);

CREATE TABLE `airbnb_listing_guests_japan_tokyo` (
  `id` varchar(200) NOT NULL,
  `first_name` varchar(200) DEFAULT NULL,
  `last_name` varchar(200) DEFAULT NULL,
  `picture_large_url` varchar(500) DEFAULT NULL,
  `gender_deepface` varchar(45) DEFAULT NULL,
  `age_deepface` varchar(45) DEFAULT NULL,
  `ethnicity_deepface` varchar(45) DEFAULT NULL,
  `gender_clarifai` varchar(45) DEFAULT NULL,
  `age_clarifai` varchar(45) DEFAULT NULL,
  `ethnicity_clarifai` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ;

CREATE TABLE `airbnb_listing_hosts_japan_tokyo` (
  `id` varchar(200) NOT NULL,
  `first_name` varchar(200) DEFAULT NULL,
  `last_name` varchar(200) DEFAULT NULL,
  `picture_large_url` varchar(500) DEFAULT NULL,
  `gender_deepface` varchar(45) DEFAULT NULL,
  `age_deepface` varchar(45) DEFAULT NULL,
  `ethnicity_deepface` varchar(45) DEFAULT NULL,
  `gender_clarifai` varchar(45) DEFAULT NULL,
  `age_clarifai` varchar(45) DEFAULT NULL,
  `ethnicity_clarifai` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ;

CREATE TABLE `airbnb_listing_review_japan_tokyo` (
  `id` bigint NOT NULL,
  `listing_id` bigint DEFAULT NULL,
  `host_id` bigint DEFAULT NULL,
  `guest_id` bigint DEFAULT NULL,
  `rating` bigint DEFAULT NULL,
  `createdAt` text,
  PRIMARY KEY (`id`)
) ;
